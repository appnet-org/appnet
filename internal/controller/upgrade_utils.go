/*
Copyright 2024.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controller

import (
	"os"
	"strconv"
)

// updateVersionFile updates the specified file with the given version number.
func updateVersionFile(filename string, version int) error {
	// Convert the version number to a string.
	versionStr := strconv.Itoa(version)

	// Write the version number to the file.
	err := os.WriteFile(filename, []byte(versionStr), 0644)
	if err != nil {
		return err
	}
	return nil
}
