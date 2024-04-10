/*
Copyright © 2023 AppNet
*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// versionCmd represents the version command
var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Get appnetctl version",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Version: v0.1.0")
	},
}

func init() {
	rootCmd.AddCommand(versionCmd)
}
