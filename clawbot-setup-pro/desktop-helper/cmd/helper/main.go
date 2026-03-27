package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("clawbot-setup-helper\n\nCommands:\n  health\n  pair <code>\n  run <plan.json>")
		os.Exit(0)
	}

	switch os.Args[1] {
	case "health":
		fmt.Println("ok")
	case "pair":
		fmt.Println("pair: not implemented")
	case "run":
		fmt.Println("run: not implemented")
	default:
		fmt.Println("unknown command")
		os.Exit(2)
	}
}
