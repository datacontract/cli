package datacontract

import (
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
)

func PrintQuality(dataContractLocation string, pathToQuality []string, target io.Writer) error {

	dataContract, err := GetDataContract(dataContractLocation)
	if err != nil {
		return fmt.Errorf("failed parsing local data contract: %w", err)
	}

	qualitySpecification, err := getQualitySpecification(dataContract, pathToQuality)
	if err != nil {
		return fmt.Errorf("can't get specification: %w", err)
	}

	Log(target, string(qualitySpecification))

	return nil
}

func InsertQuality(
	dataContractLocation string,
	qualitySpecification []byte,
	qualityType string,
	pathToQuality []string,
	pathToType []string,
) error {
	contract, err := GetDataContract(dataContractLocation)
	if err != nil {
		return err
	}

	SetValue(contract, pathToQuality, string(qualitySpecification))
	SetValue(contract, pathToType, qualityType)

	result, err := ToYaml(contract)
	if err != nil {
		return err
	}

	err = os.WriteFile(dataContractLocation, result, os.ModePerm)
	if err != nil {
		return err
	}

	return nil
}

type QualityCheckOptions struct {
	SodaDataSource            *string
	SodaConfigurationFileName *string
}

func QualityCheck(
	dataContractFileName string,
	pathToType []string,
	pathToSpecification []string,
	options QualityCheckOptions,
	target io.Writer,
) error {

	contract, err := GetDataContract(dataContractFileName)
	if err != nil {
		return fmt.Errorf("quality checks failed: %w", err)
	}

	qualityType, err := getQualityType(contract, pathToType)
	if err != nil {
		return fmt.Errorf("quality type cannot be retrieved: %w", err)
	}

	if qualityType != "SodaCL" {
		log.Printf("The '%s' quality type is not supported yet", qualityType)
		return nil
	}

	qualitySpecification, err := getQualitySpecification(contract, pathToSpecification)
	if err != nil {
		return fmt.Errorf("quality check specification cannot be retrieved: %w",
			err)
	}

	tempFile, err := os.CreateTemp("", "quality-checks-")
	if err != nil {
		return fmt.Errorf("can not create temporary file for quality checks: %w", err)
	}

	tempFile.Write(qualitySpecification)

	err = sodaQualityCheck(tempFile.Name(), options, target)

	printQualityChecksResult(err, target)

	if err != nil {
		return fmt.Errorf("quality checks failed: %w", err)
	}

	tempFile.Close()

	return nil
}

func printQualityChecksResult(err error, target io.Writer) {
	if err == nil {
		Log(target, "🟢 quality checks on data contract passed!")
	} else {
		Log(target, "🔴 quality checks on data contract failed!")
	}
}

func getQualityType(
	contract DataContract,
	path []string) (qualityType string, err error) {
	qualityTypeUntyped, err := GetValue(contract, path)
	if err != nil {
		return "",
			fmt.Errorf("can't get value of quality type: %w for path %v",
				err, path)
	}

	qualityType, ok := qualityTypeUntyped.(string)
	if !ok {
		return "", fmt.Errorf("quality not of type string")
	}

	return qualityType, nil
}

func getQualitySpecification(
	contract DataContract,
	path []string) (specification []byte, err error) {
	spec, err := GetValue(contract, path)
	if err != nil {
		return []byte{},
			fmt.Errorf("can't get value of %w quality specification for path %v",
				err, path)
	}

	return TakeStringOrMarshall(spec), nil
}

// soda core checks

func sodaQualityCheck(qualitySpecFileName string, options QualityCheckOptions, target io.Writer) error {
	var args = []string{"scan"}

	args = append(args, "-d")
	if options.SodaDataSource != nil {
		args = append(args, *options.SodaDataSource)
	} else {
		args = append(args, "default")
	}

	if options.SodaConfigurationFileName != nil {
		args = append(args, "-c")
		args = append(args, *options.SodaConfigurationFileName)
	}

	args = append(args, qualitySpecFileName)

	cmd := exec.Command("soda", args...)
	output, err := cmdCombinedOutput(cmd)

	Log(target, string(output))

	if err != nil {
		return fmt.Errorf("the soda CLI failed: %w", err)
	}

	return nil
}
