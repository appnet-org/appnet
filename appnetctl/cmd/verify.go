/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"bytes"
	"fmt"
	"os/exec"
	"strconv"
	"strings"

	"github.com/spf13/cobra"
)

// execCommand executes a given command and returns its output or an error.
func execCommand(command string, args ...string) (string, error) {
	cmd := exec.Command(command, args...)
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	if err != nil {
		return "", err
	}
	return out.String(), nil
}

func isVersionGreaterThan(version string, major, minor int) (bool, error) {
	// Split version string on spaces (e.g., "Python 3.9.1") and then on dots
	parts := strings.Split(version, " ")
	if len(parts) < 2 {
		return false, fmt.Errorf("unexpected version format")
	}
	versionParts := strings.Split(parts[1], ".")
	if len(versionParts) < 2 {
		return false, fmt.Errorf("unexpected version format")
	}

	// Convert version parts to integers
	majorVersion, err := strconv.Atoi(versionParts[0])
	if err != nil {
		return false, err
	}
	minorVersion, err := strconv.Atoi(versionParts[1])
	if err != nil {
		return false, err
	}

	// Compare with specified major and minor versions
	return majorVersion > major || (majorVersion == major && minorVersion >= minor), nil
}

// verifyCmd represents the verify command
var verifyCmd = &cobra.Command{
	Use:   "verify",
	Short: "Verifies AppNet Installation Status",
	// 	Long: `A longer description that spans multiple lines and likely contains examples
	// and usage of using your command. For example:

	// Cobra is a CLI library for Go that empowers applications.
	// This application is a tool to generate the needed files
	// to quickly create a Cobra application.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Verifying AppNet installation status...")

		// Check if Python version is greater than 3.10
		pythonVersion, err := execCommand("python", "--version")
		if err == nil {
			isGreater, err := isVersionGreaterThan(pythonVersion, 3, 10)
			if err != nil {
				fmt.Printf("✘ Failed to parse Python version: %s\n", err)
			} else if isGreater {
				fmt.Printf("✔ Python installed.\n")
			} else {
				fmt.Printf("✘ Python version is not greater than 3.10: %s\n", pythonVersion)
			}
		} else {
			fmt.Println("✘ Python is not installed.")
		}

		// Verify Rust installation
		_, err = execCommand("rustc", "--version")
		if err == nil {
			fmt.Printf("✔ Rust installed.\n")
		} else {
			fmt.Println("✘ Rust is not installed.")
		}

		// Verify Kubernetes installation
		_, err = execCommand("kubectl", "version")
		if err == nil {
			fmt.Printf("✔ Kubernetes installed.\n")
		} else {
			fmt.Println("✘ Kubernetes is not installed.")
		}

		// Verify protoc installation
		_, err = execCommand("protoc", "--version")
		if err == nil {
			fmt.Printf("✔ protoc installed.\n")
		} else {
			fmt.Println("✘ protoc is not installed.")
		}
	},
}

func init() {
	rootCmd.AddCommand(verifyCmd)
}
