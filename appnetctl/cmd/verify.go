/*
Copyright © 2024 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"bytes"
	"fmt"
	"os/exec"
	"regexp"
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
	versionParts := strings.Split(version, ".")
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

func isExactVersion(version string, major, minor, patch int) (bool, error) {
	versionParts := strings.Split(version, ".")
	if len(versionParts) < 3 {
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
	patchVersion, err := strconv.Atoi(versionParts[2])
	if err != nil {
		return false, err
	}

	// Check if version matches exactly
	return majorVersion == major && minorVersion == minor && patchVersion == patch, nil
}

// verifyCmd represents the verify command
var verifyCmd = &cobra.Command{
	Use:   "verify",
	Short: "Verifies AppNet Installation Status",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("Verifying AppNet installation status...")

		// Check if Python version is greater than 3.10
		pythonVersion, err := execCommand("python", "--version")
		if err == nil {
			// Parse Python Version
			parts := strings.Split(pythonVersion, " ")
			if len(parts) < 2 {
				fmt.Println("unexpected Python version format")
			}

			isGreater, err := isVersionGreaterThan(parts[1], 3, 10)
			if err != nil {
				fmt.Printf("✘ Failed to parse Python version: %s\n", err)
			} else if isGreater {
				fmt.Println("✔ Python installed.")
			} else {
				fmt.Printf("✘ Python version is not greater than 3.10: %s", pythonVersion)
			}
		} else {
			fmt.Println("✘ Python is not installed.")
		}

		// Verify Rust installation
		_, err = execCommand("rustc", "--version")
		if err == nil {
			fmt.Println("✔ Rust installed.")
		} else {
			fmt.Println("✘ Rust is not installed.")
		}

		// Verify Kubernetes installation
		kubectlVersion, err := execCommand("kubectl", "version")
		if err == nil {
			// Parse kubectl Version
			re := regexp.MustCompile(`Client Version: v(\d+\.\d+\.\d+)`)

			// Find the version number in the output
			matches := re.FindStringSubmatch(kubectlVersion)
			if len(matches) < 2 {
				fmt.Println("Version number not found")
				return
			}

			isGreater, err := isVersionGreaterThan(matches[1], 1, 28)
			if err != nil {
				fmt.Printf("✘ Failed to parse kubectl version: %s\n", err)
			} else if isGreater {
				fmt.Println("✔ Kubernetes installed.")
			} else {
				fmt.Printf("✘ Kubernetes version is not greater than 1.28.0: %s", kubectlVersion)
			}
		} else {
			fmt.Println("✘ Kubernetes is not installed.")
		}

		// Verify protoc installation
		_, err = execCommand("protoc", "--version")
		if err == nil {
			fmt.Println("✔ protoc installed.")
		} else {
			fmt.Println("✘ protoc is not installed.")
		}

		// Verify istio installation
		istioctlVersion, err := execCommand("istioctl", "version")
		if err == nil {
			// Parse istioctl Version
			re := regexp.MustCompile(`client version: (\d+\.\d+\.\d+)`)

			// Find the version number in the output
			matches := re.FindStringSubmatch(istioctlVersion)
			if len(matches) < 2 {
				fmt.Println("Version number not found")
				return
			}

			isGreater, err := isVersionGreaterThan(matches[1], 1, 22)
			if err != nil {
				fmt.Printf("✘ Failed to parse istioctl version: %s\n", err)
			} else if isGreater {
				fmt.Println("✔ Istio installed.")
			} else {
				fmt.Printf("✘ Istio version is not greater than 1.22.0: %s", istioctlVersion)
			}
		} else {
			fmt.Println("✘ Istio is not installed.")
		}

		// Verify Go installation and version
		goVersion, err := execCommand("go", "version")
		if err == nil {
			// Parse Go Version
			re := regexp.MustCompile(`go version go(\d+\.\d+\.\d+)`)

			// Find the version number in the output
			matches := re.FindStringSubmatch(goVersion)
			if len(matches) < 2 {
				fmt.Println("Version number not found")
				return
			}

			isExact, err := isExactVersion(matches[1], 1, 22, 1)
			if err != nil {
				fmt.Printf("✘ Failed to parse Go version: %s\n", err)
			} else if isExact {
				fmt.Println("✔ Go version 1.22.1 installed.")
			} else {
				fmt.Printf("✘ Go version is not 1.22.1: %s", goVersion)
			}
		} else {
			fmt.Println("✘ Go is not installed.")
		}
	},
}

func init() {
	rootCmd.AddCommand(verifyCmd)
}
