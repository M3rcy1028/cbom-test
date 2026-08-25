package main

import (
	"bytes"
	"crypto/mlkem"
	"fmt"
)

// mlkem768RoundTrip performs an actual ML-KEM-768 encapsulation and
// decapsulation using Go's FIPS 203 implementation. This is a small CBOM
// scanner fixture; production systems still need protocol-level key handling.
func mlkem768RoundTrip() int {
	decapsulationKey, err := mlkem.GenerateKey768()
	if err != nil {
		panic(err)
	}

	encapsulationKey := decapsulationKey.EncapsulationKey()
	senderSharedKey, ciphertext := encapsulationKey.Encapsulate()
	receiverSharedKey, err := decapsulationKey.Decapsulate(ciphertext)
	if err != nil {
		panic(err)
	}
	if !bytes.Equal(senderSharedKey, receiverSharedKey) {
		panic("ML-KEM-768 shared keys do not match")
	}

	return len(senderSharedKey)
}

func main() {
	sharedKeyBytes := mlkem768RoundTrip()
	fmt.Printf(
		"quantum-safe-fixture-ok algorithm=ML-KEM-768 shared-key-bytes=%d\n",
		sharedKeyBytes,
	)
}
