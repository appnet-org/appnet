/*
Copyright © 2023 NAME HERE <EMAIL ADDRESS>

*/
package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// versionCmd represents the version command
var versionCmd = &cobra.Command{
	Use:   "version",
	Short: "Get adnctl version",
	Run: func(cmd *cobra.Command, args []string) {
		// Placeholder
		fmt.Println("Version: Experimental")
	},
}

func init() {
	rootCmd.AddCommand(versionCmd)
}
