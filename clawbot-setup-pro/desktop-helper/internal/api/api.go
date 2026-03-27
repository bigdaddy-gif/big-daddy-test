package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type Client struct {
	BaseURL    string
	HTTP       *http.Client
	DeviceID   string
	DeviceToken string
}

func New(baseURL string) *Client {
	return &Client{
		BaseURL: baseURL,
		HTTP: &http.Client{Timeout: 30 * time.Second},
	}
}

type ActivateRequest struct {
	Code     string `json:"code"`
	Name     string `json:"name"`
	Platform string `json:"platform"`
}

type ActivateResponse struct {
	DeviceID    string `json:"device_id"`
	DeviceToken string `json:"device_token"`
}

func (c *Client) Activate(code, name, platform string) error {
	body, _ := json.Marshal(ActivateRequest{Code: code, Name: name, Platform: platform})
	req, err := http.NewRequest("POST", c.BaseURL+"/v1/devices/activate", bytes.NewReader(body))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := c.HTTP.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		return fmt.Errorf("activate failed: %s", resp.Status)
	}
	var out ActivateResponse
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return err
	}
	c.DeviceID = out.DeviceID
	c.DeviceToken = out.DeviceToken
	return nil
}

func (c *Client) authReq(method, path string, payload any) (*http.Request, error) {
	var r *http.Request
	var err error
	if payload != nil {
		b, _ := json.Marshal(payload)
		r, err = http.NewRequest(method, c.BaseURL+path, bytes.NewReader(b))
		r.Header.Set("Content-Type", "application/json")
	} else {
		r, err = http.NewRequest(method, c.BaseURL+path, nil)
	}
	if err != nil {
		return nil, err
	}
	if c.DeviceToken != "" {
		r.Header.Set("Authorization", "Bearer "+c.DeviceToken)
	}
	return r, nil
}

func (c *Client) Heartbeat() error {
	req, err := c.authReq("POST", fmt.Sprintf("/v1/devices/%s/heartbeat", c.DeviceID), map[string]any{},)
	if err != nil {
		return err
	}
	resp, err := c.HTTP.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		return fmt.Errorf("heartbeat failed: %s", resp.Status)
	}
	return nil
}

type LogIn struct {
	Level   string `json:"level"`
	Message string `json:"message"`
}

func (c *Client) Log(level, msg string) {
	_ = c.postLog(level, msg)
}

func (c *Client) postLog(level, msg string) error {
	req, err := c.authReq("POST", fmt.Sprintf("/v1/devices/%s/logs", c.DeviceID), LogIn{Level: level, Message: msg})
	if err != nil {
		return err
	}
	resp, err := c.HTTP.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}

type PollResponse struct {
	Commands []struct {
		ID     string         `json:"id"`
		JobID  string         `json:"job_id"`
		Kind   string         `json:"kind"`
		Payload map[string]any `json:"payload"`
	} `json:"commands"`
}

func (c *Client) Poll() (*PollResponse, error) {
	req, err := c.authReq("POST", fmt.Sprintf("/v1/devices/%s/poll", c.DeviceID), map[string]any{})
	if err != nil {
		return nil, err
	}
	resp, err := c.HTTP.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		return nil, fmt.Errorf("poll failed: %s", resp.Status)
	}
	var out PollResponse
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return nil, err
	}
	return &out, nil
}

type ProgressIn struct {
	Progress int    `json:"progress"`
	Message  string `json:"message,omitempty"`
}

func (c *Client) JobProgress(jobID string, pct int, msg string) {
	_, _ = c.JobProgressErr(jobID, pct, msg)
}

func (c *Client) JobProgressErr(jobID string, pct int, msg string) (*http.Response, error) {
	req, err := c.authReq("POST", fmt.Sprintf("/v1/jobs/%s/progress", jobID), ProgressIn{Progress: pct, Message: msg})
	if err != nil {
		return nil, err
	}
	return c.HTTP.Do(req)
}

type CompleteIn struct {
	Status string         `json:"status"`
	Result map[string]any `json:"result,omitempty"`
}

func (c *Client) JobComplete(jobID string, status string, result map[string]any) {
	req, err := c.authReq("POST", fmt.Sprintf("/v1/jobs/%s/complete", jobID), CompleteIn{Status: status, Result: result})
	if err != nil {
		return
	}
	resp, _ := c.HTTP.Do(req)
	if resp != nil {
		resp.Body.Close()
	}
}
