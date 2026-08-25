package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/ecdh"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha256"
	"fmt"
)

var data = []byte("cbom-lab-fixture")

func aesGCM() []byte {
	block, _ := aes.NewCipher(make([]byte, 16))
	gcm, _ := cipher.NewGCM(block)
	return gcm.Seal(nil, make([]byte, gcm.NonceSize()), data, nil)
}

func rsaOAEP() []byte {
	privateKey, _ := rsa.GenerateKey(rand.Reader, 2048)
	output, _ := rsa.EncryptOAEP(sha256.New(), rand.Reader, &privateKey.PublicKey, data, nil)
	return output
}

func hashes() ([]byte, []byte) {
	sha := sha256.Sum256(data)
	replacement := sha256.Sum256(data)
	return sha[:], replacement[:]
}

func ecdsaSign() []byte {
	key, _ := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	digest := sha256.Sum256(data)
	signature, _ := ecdsa.SignASN1(rand.Reader, key, digest[:])
	return signature
}

func ecdhSecret() []byte {
	curve := ecdh.P256()
	alice, _ := curve.GenerateKey(rand.Reader)
	bob, _ := curve.GenerateKey(rand.Reader)
	secret, _ := alice.ECDH(bob.PublicKey())
	return secret
}

func main() {
	sha, replacement := hashes()
	outputs := [][]byte{aesGCM(), rsaOAEP(), sha, replacement, ecdsaSign(), ecdhSecret()}
	for _, output := range outputs {
		if len(output) == 0 {
			panic("empty fixture output")
		}
	}
	fmt.Println("go-fixture-ok", len(outputs))
}
