package lab;

import java.nio.charset.StandardCharsets;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.security.Signature;
import java.security.spec.ECGenParameterSpec;
import java.util.Arrays;
import javax.crypto.Cipher;
import javax.crypto.KeyAgreement;
import javax.crypto.SecretKey;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * Deliberately diverse cryptographic calls for CBOM scanner evaluation.
 * This is a test fixture, not production cryptographic guidance.
 */
public final class CryptoFixture {
    private static final byte[] DATA = "cbom-lab-fixture".getBytes(StandardCharsets.UTF_8);

    private CryptoFixture() {}

    public static byte[] aesGcm() throws Exception {
        SecretKey key = new SecretKeySpec(new byte[16], "AES");
        GCMParameterSpec params = new GCMParameterSpec(128, new byte[12]);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key, params);
        return cipher.doFinal(DATA);
    }

    public static byte[] aesGcmSecondary() throws Exception {
        SecretKey key = new SecretKeySpec(new byte[16], "AES");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, new byte[12]));
        return cipher.doFinal(DATA);
    }

    public static byte[] rsaOaep() throws Exception {
        KeyPairGenerator generator = KeyPairGenerator.getInstance("RSA");
        generator.initialize(2048);
        KeyPair pair = generator.generateKeyPair();
        Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding");
        cipher.init(Cipher.ENCRYPT_MODE, pair.getPublic());
        return cipher.doFinal(DATA);
    }

    public static byte[] sha256() throws Exception {
        return MessageDigest.getInstance("SHA-256").digest(DATA);
    }

    public static byte[] sha256Replacement() throws Exception {
        return MessageDigest.getInstance("SHA-256").digest(DATA);
    }

    public static byte[] pbkdf2() throws Exception {
        PBEKeySpec spec = new PBEKeySpec("test-only".toCharArray(), new byte[16], 120_000, 256);
        return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
                .generateSecret(spec)
                .getEncoded();
    }

    public static byte[] ecdsa() throws Exception {
        KeyPairGenerator generator = KeyPairGenerator.getInstance("EC");
        generator.initialize(new ECGenParameterSpec("secp256r1"), new SecureRandom());
        KeyPair pair = generator.generateKeyPair();
        Signature signature = Signature.getInstance("SHA256withECDSA");
        signature.initSign(pair.getPrivate());
        signature.update(DATA);
        return signature.sign();
    }

    public static byte[] ecdh() throws Exception {
        KeyPairGenerator generator = KeyPairGenerator.getInstance("EC");
        generator.initialize(new ECGenParameterSpec("secp256r1"));
        KeyPair alice = generator.generateKeyPair();
        KeyPair bob = generator.generateKeyPair();
        KeyAgreement agreement = KeyAgreement.getInstance("ECDH");
        agreement.init(alice.getPrivate());
        agreement.doPhase(bob.getPublic(), true);
        return agreement.generateSecret();
    }

    public static void main(String[] args) throws Exception {
        int[] lengths = {
            aesGcm().length,
            aesGcmSecondary().length,
            rsaOaep().length,
            sha256().length,
            sha256Replacement().length,
            pbkdf2().length,
            ecdsa().length,
            ecdh().length
        };
        if (Arrays.stream(lengths).anyMatch(length -> length == 0)) {
            throw new IllegalStateException("A fixture produced empty output");
        }
        System.out.println("java-fixture-ok " + Arrays.toString(lengths));
    }
}
