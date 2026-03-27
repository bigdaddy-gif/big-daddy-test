package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"runtime"
	"time"

	"github.com/bigdaddy-gif/big-daddy-test/clawbot-setup-pro/desktop-helper/internal/api"
	"github.com/bigdaddy-gif/big-daddy-test/clawbot-setup-pro/desktop-helper/internal/runner"
)

type report struct {
	c     *api.Client
	jobID string
}

func (r *report) Log(level, msg string) {
	r.c.Log(level, msg)
}

func (r *report) Progress(pct int, msg string) {
	r.c.JobProgress(r.jobID, pct, msg)
	if msg != "" {
		r.c.Log("info", msg)
	}
}

func main() {
	baseURL := flag.String("base-url", "http://localhost:8000", "Backend base URL")
	flag.Parse()

	args := flag.Args()
	if len(args) < 1 {
		fmt.Println("clawbot-setup-helper\n\nCommands:\n  activate <pairing_code> --name <name> --platform <windows|macos>\n  loop --device-id <id> --device-token <token>\n")
		os.Exit(0)
	}

	cmd := args[0]
	switch cmd {
	case "activate":
		fs := flag.NewFlagSet("activate", flag.ExitOnError)
		name := fs.String("name", "My Computer", "Device name")
		platform := fs.String("platform", runtime.GOOS, "windows|macos")
		_ = fs.Parse(args[1:])
		rest := fs.Args()
		if len(rest) < 1 {
			fmt.Println("missing pairing code")
			os.Exit(2)
		}
		code := rest[0]

		c := api.New(*baseURL)
		if err := c.Activate(code, *name, *platform); err != nil {
			fmt.Println(err)
			os.Exit(1)
		}
		fmt.Printf("device_id=%s\ndevice_token=%s\n", c.DeviceID, c.DeviceToken)

	case "loop":
		fs := flag.NewFlagSet("loop", flag.ExitOnError)
		deviceID := fs.String("device-id", "", "Device ID")
		deviceToken := fs.String("device-token", "", "Device token")
		_ = fs.Parse(args[1:])
		if *deviceID == "" || *deviceToken == "" {
			fmt.Println("missing --device-id or --device-token")
			os.Exit(2)
		}

		c := api.New(*baseURL)
		c.DeviceID = *deviceID
		c.DeviceToken = *deviceToken

		ctx := context.Background()
		ticker := time.NewTicker(30 * time.Second)
		defer ticker.Stop()

		c.Log("info", "helper online")

		for {
			_ = c.Heartbeat()

			poll, err := c.Poll()
			if err == nil && poll != nil {
				for _, cmd := range poll.Commands {
					if cmd.Kind == "run_plan" {
						jobID := cmd.JobID
						payload := cmd.Payload
						planAny := payload["plan"]
						b, _ := json.Marshal(planAny)
						var plan runner.Plan
						_ = json.Unmarshal(b, &plan)

						rep := &report{c: c, jobID: jobID}
						err := runner.RunPlan(ctx, plan, rep)
						if err != nil {
							c.JobComplete(jobID, "failed", map[string]any{"error": err.Error()})
						} else {
							c.JobComplete(jobID, "succeeded", map[string]any{"ok": true})
						}
					}
				}
			}

			select {
			case <-ticker.C:
				continue
			default:
				time.Sleep(2 * time.Second)
			}
		}

	default:
		fmt.Println("unknown command")
		os.Exit(2)
	}
}
