package main

import (
	"crypto/mlkem"
	"testing"
)

func TestMLKEM768RoundTrip(t *testing.T) {
	if got := mlkem768RoundTrip(); got != mlkem.SharedKeySize {
		t.Fatalf("shared key length = %d, want %d", got, mlkem.SharedKeySize)
	}
}
