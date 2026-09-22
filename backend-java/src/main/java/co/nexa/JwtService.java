package co.nexa;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Date;

@Service
public class JwtService {
    private final SecretKey key;
    public JwtService(@Value("${nexa.jwt-secret}") String secret) {
        key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }
    public String create(String userId, String role) {
        Instant now = Instant.now();
        return Jwts.builder().subject(userId).claim("role", role)
                .issuedAt(Date.from(now)).expiration(Date.from(now.plusSeconds(86_400)))
                .signWith(key).compact();
    }
}
