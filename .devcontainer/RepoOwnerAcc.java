import java.security.MessageDigest;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

public class RepoOwnerAccess {

    static class OwnerIdentity {
        private final String ownerId;
        private final String ownerName;
        private final String ownerEmail;
        private final String accessKey;
        private final LocalDateTime createdAt;
        private boolean isActive;

        public OwnerIdentity(String ownerName, String ownerEmail) {
            this.ownerId = generateOwnerId();
            this.ownerName = ownerName;
            this.ownerEmail = ownerEmail;
            this.accessKey = generateAccessKey();
            this.createdAt = LocalDateTime.now();
            this.isActive = true;
        }

        private String generateOwnerId() {
            SecureRandom random = new SecureRandom();
            byte[] bytes = new byte[16];
            random.nextBytes(bytes);
            return "OWN-" + Base64.getUrlEncoder().withoutPadding()
                    .encodeToString(bytes).substring(0, 12).toUpperCase();
        }

        private String generateAccessKey() {
            SecureRandom random = new SecureRandom();
            byte[] bytes = new byte[32];
            random.nextBytes(bytes);
            return Base64.getUrlEncoder().withoutPadding()
                    .encodeToString(bytes).substring(0, 24);
        }

        public String getOwnerId() { return ownerId; }
        public String getOwnerName() { return ownerName; }
        public String getAccessKey() { return accessKey; }
        public boolean isActive() { return isActive; }
        public void deactivate() { this.isActive = false; }
    }

    static class AccessFramework {
        private final Map<String, OwnerIdentity> owners = new HashMap<>();
        private final Map<String, String> activeTokens = new HashMap<>();

        public OwnerIdentity registerOwner(String name, String email) {
            OwnerIdentity owner = new OwnerIdentity(name, email);
            owners.put(owner.getOwnerId(), owner);
            System.out.println("[OK] Registered: " + owner.getOwnerId());
            return owner;
        }

        public String generateLink(OwnerIdentity owner, String baseUrl) {
            if (!owner.isActive()) {
                System.out.println("[DENIED] Owner inactive.");
                return null;
            }
            String token = createToken(owner);
            activeTokens.put(token, owner.getOwnerId());
            String url = baseUrl + "?owner_id=" + owner.getOwnerId() + "&token=" + token;
            System.out.println("[OK] Link generated.");
            return url;
        }

        public boolean validate(String ownerId, String token) {
            String storedOwner = activeTokens.get(token);
            if (storedOwner == null || !storedOwner.equals(ownerId)) {
                System.out.println("[DENIED] Invalid access.");
                return false;
            }
            System.out.println("[GRANTED] Access verified.");
            return true;
        }

        public void revoke(String token) {
            activeTokens.remove(token);
            System.out.println("[OK] Access revoked.");
        }

        private String createToken(OwnerIdentity owner) {
            try {
                String data = owner.getOwnerId() + ":" + owner.getAccessKey()
                        + ":" + System.currentTimeMillis();
                MessageDigest digest = MessageDigest.getInstance("SHA-256");
                byte[] hash = digest.digest(data.getBytes());
                return Base64.getUrlEncoder().withoutPadding()
                        .encodeToString(hash).substring(0, 20);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }
    }

    public static void main(String[] args) {
        AccessFramework framework = new AccessFramework();

        System.out.println("═══════════════════════════════════════════");
        System.out.println("  REPO OWNER ACCESS CONTROL");
        System.out.println("═══════════════════════════════════════════\n");

        OwnerIdentity owner = framework.registerOwner(
                "Danial Zivehdar",
                "danialzivehdar1992@gmail.com"
        );

        System.out.println("\n  Owner ID   : " + owner.getOwnerId());
        System.out.println("  Access Key : " + owner.getAccessKey());

        String link = framework.generateLink(owner,
                "https://your-repo.com/direct-access");

        System.out.println("\n  Direct Link:\n  " + link);

        System.out.println("\n───────────────────────────────────────────");
        System.out.println("  Validation Test:");
        System.out.println("───────────────────────────────────────────");

        framework.validate(owner.getOwnerId(),
                link.split("token=")[1]);

        framework.validate("OWN-FAKE000000",
                link.split("token=")[1]);

        System.out.println("\n═══════════════════════════════════════════");
    }
}
