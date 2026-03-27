package runner

import (
	"bufio"
	"context"
	"fmt"
	"os/exec"
)

type Step struct {
	Name string `json:"name"`
	Cmd  string `json:"cmd"`
}

type Plan struct {
	Steps []Step `json:"steps"`
}

type Reporter interface {
	Log(level, msg string)
	Progress(pct int, msg string)
}

func RunPlan(ctx context.Context, plan Plan, r Reporter) error {
	n := len(plan.Steps)
	if n == 0 {
		r.Progress(100, "no steps")
		return nil
	}

	for i, s := range plan.Steps {
		pct := int(float64(i) / float64(n) * 100)
		r.Progress(pct, fmt.Sprintf("starting: %s", s.Name))
		r.Log("info", fmt.Sprintf("step %d/%d: %s", i+1, n, s.Cmd))

		cmd := exec.CommandContext(ctx, "bash", "-lc", s.Cmd)
		stdout, _ := cmd.StdoutPipe()
		stderr, _ := cmd.StderrPipe()

		if err := cmd.Start(); err != nil {
			return err
		}

		scan := func(prefix string, rd any) {
			s, ok := rd.(interface{ Read([]byte) (int, error) })
			if !ok {
				return
			}
			scanner := bufio.NewScanner(s)
			for scanner.Scan() {
				r.Log("info", prefix+scanner.Text())
			}
		}

		go scan("[stdout] ", stdout)
		go scan("[stderr] ", stderr)

		if err := cmd.Wait(); err != nil {
			r.Log("error", fmt.Sprintf("step failed: %s (%v)", s.Name, err))
			return err
		}
	}

	r.Progress(100, "complete")
	return nil
}
