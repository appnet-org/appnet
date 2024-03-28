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
		// Placeholder
		fmt.Println("Version: Experimental")
	},
}

func init() {
	rootCmd.AddCommand(versionCmd)
}
