package controller

import (
	"fmt"
	"os"

	apiv1 "github.com/appnet-org/appnet/api/v1"
	"gopkg.in/yaml.v2"
)

type AppManifest struct {
	AppName         string                       `yaml:"app_name"`
	AppManifestFile string                       `yaml:"app_manifest"`
	AppStructure    []string                     `yaml:"app_structure"`
	Edge            map[string][]EdgeElementItem `yaml:"edge"`
	Link            map[string][]PairElementItem `yaml:"link"`
}

type EdgeElementItem struct {
	Method           string   `yaml:"method"`
	Name             string   `yaml:"name"`
	Path             string   `yaml:"path"`
	Position         string   `yaml:"position"`
	Proto            string   `yaml:"proto"`
	ProtoModName     string   `yaml:"proto_mod_name"`
	ProtoModLocation string   `yaml:"proto_mod_location"`
	Upgrade          bool     `yaml:"upgrade"`
	Processors       []string `yaml:"processors"`
}

type PairElementItem struct {
	Method   string `yaml:"method"`
	Name1    string `yaml:"name1"`
	Name2    string `yaml:"name2"`
	Position string `yaml:"position"`
	Proto    string `yaml:"proto"`
}

func ConvertToAppNetSpec(appName, appManifestFile, clientService, serverService, method, proto, fileName, protoModName, protoModLocation string, processors []string, clientChain, serverChain, anyChain, pairChain []apiv1.ChainElement) error {
	clientServerTag := fmt.Sprintf("%s->%s", clientService, serverService)

	appManifest := AppManifest{
		AppName:         appName,
		AppManifestFile: appManifestFile,
		AppStructure: []string{
			clientServerTag,
		},
		Edge: make(map[string][]EdgeElementItem),
		Link: make(map[string][]PairElementItem),
	}

	position := ""
	if len(clientChain) > 0 {
		for _, element := range clientChain {
			appManifest.Edge[clientServerTag] = append(appManifest.Edge[clientServerTag], EdgeElementItem{
				Method:           method,
				Name:             element.Name,
				Position:         position,
				Proto:            proto,
				Path:             element.File,
				ProtoModName:     protoModName,
				ProtoModLocation: protoModLocation,
				Upgrade:          element.Upgrade,
				Processors:       processors,
			})
		}
	}

	if len(serverChain) > 0 {
		for _, element := range serverChain {
			appManifest.Edge[clientServerTag] = append(appManifest.Edge[clientServerTag], EdgeElementItem{
				Method:           method,
				Name:             element.Name,
				Position:         "server",
				Proto:            proto,
				Path:             element.File,
				ProtoModName:     protoModName,
				ProtoModLocation: protoModLocation,
				Upgrade:          element.Upgrade,
				Processors:       processors,
			})
		}
	}

	if len(anyChain) > 0 {
		for _, element := range anyChain {
			appManifest.Edge[clientServerTag] = append(appManifest.Edge[clientServerTag], EdgeElementItem{
				Method:           method,
				Name:             element.Name,
				Position:         position,
				Proto:            proto,
				Path:             element.File,
				ProtoModName:     protoModName,
				ProtoModLocation: protoModLocation,
				Upgrade:          element.Upgrade,
				Processors:       processors,
			})
		}
	}

	// // TODO: Update pairChain parsing logic
	// if len(pairChain) > 0 {
	// 	pair_elements := strings.Split(pairChain, "->")
	// 	for _, element := range pair_elements {
	// 		// Modify as needed to specify different elements for Name1 and Name2
	// 		appManifest.Link[clientServerTag] = append(appManifest.Link[clientServerTag], PairElementItem{
	// 			Method: method,
	// 			Name1:  removeParentheses(element),
	// 			Name2:  removeParentheses(element), // Modify as needed
	// 			Proto:  proto,
	// 		})
	// 	}
	// }

	yamlBytes, err := yaml.Marshal(&appManifest)
	if err != nil {
		return err
	}

	file, err := os.Create(fileName)
	if err != nil {
		return err
	}
	defer file.Close()

	_, err = file.Write(yamlBytes)
	if err != nil {
		return err
	}

	return nil
}

// func main() {
// 	clientService := "frontend"
// 	serverService := "ping"
// 	name := "ping"
// 	method := "PingEcho"
// 	clientChain := "rate()->fault()"
// 	serverChain := "admission()->loadbalance()"
// 	anyChain := "metrics()->tracing()"
// 	pairChain := "encrypt()->decrypt()"
// 	proto := "examples/proto/ping.proto"
// 	fileName := "output.yaml"

// 	err := GenerateAndWriteYAMLToFile(clientService, serverService, clientChain, serverChain, anyChain, pairChain, name, method, proto, fileName)
// 	if err != nil {
// 		fmt.Printf("Error: %v\n", err)
// 		return
// 	}

// 	fmt.Printf("YAML written to %s\n", fileName)
// }
