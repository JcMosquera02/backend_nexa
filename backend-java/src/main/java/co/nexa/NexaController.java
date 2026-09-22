package co.nexa;

import jakarta.validation.Valid;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import java.time.Instant;
import java.util.*;

@RestController
public class NexaController {
  private final JdbcTemplate db; private final PasswordEncoder encoder;
  public NexaController(JdbcTemplate db, PasswordEncoder encoder){this.db=db;this.encoder=encoder;}
  public record Register(@NotBlank String cedula,@NotBlank String nombreCompleto,@Email String correo,@NotBlank String password,String role,boolean consentimientoDatos){}
  public record Login(@Email String correo,@NotBlank String password){}
  @GetMapping("/health") Map<String,String> health(){return Map.of("status","ok","service","NEXA Spring Boot");}
  @GetMapping("/api/dashboard/summary") Map<String,Object> summary(){return Map.of("accessesToday",count("SELECT count(*) FROM accesos WHERE ocurrio_en >= now() - interval '1 day'"),"activeAlerts",count("SELECT count(*) FROM alertas WHERE estado <> 'cerrada'"),"onlineCameras",count("SELECT count(*) FROM camaras WHERE activa = true"),"registeredPeople",count("SELECT count(*) FROM usuarios WHERE activo = true"));}
  @GetMapping("/api/accesos") List<Map<String,Object>> accesses(){return db.queryForList("SELECT a.id, u.nombre_completo AS usuario, a.tipo_credencial AS credential, a.punto_acceso AS point, a.ocurrio_en AS time, CASE WHEN a.resultado='permitido' THEN 'Permitido' ELSE 'Denegado' END AS status FROM accesos a JOIN usuarios u ON u.id=a.usuario_id ORDER BY a.ocurrio_en DESC LIMIT 100");}
  @PostMapping("/api/accesos") @ResponseStatus(HttpStatus.CREATED) Map<String,Object> createAccess(@RequestBody Map<String,Object> input){String userId=String.valueOf(input.get("usuario_id"));if(count("SELECT count(*) FROM usuarios WHERE id = '"+userId+"'::uuid AND activo=true") == 0) throw new ResponseStatusException(HttpStatus.FORBIDDEN,"No permitir acceso: usuario inexistente o inactivo");db.update("INSERT INTO accesos(usuario_id,tipo_credencial,punto_acceso,placa_vehiculo,resultado) VALUES (?::uuid,?,?,?,?)",userId,input.get("tipo_credencial"),input.get("punto_acceso"),input.get("placa_vehiculo"),input.getOrDefault("resultado","permitido"));return Map.of("status","registered");}
  @GetMapping("/api/alertas") List<Map<String,Object>> alerts(){return db.queryForList("SELECT id,tipo,severidad,descripcion,estado,creada_en AS \"creadaEn\" FROM alertas ORDER BY creada_en DESC LIMIT 10");}
  @PostMapping("/api/alertas") @ResponseStatus(HttpStatus.CREATED) Map<String,Object> createAlert(@RequestBody Map<String,Object> input){db.update("INSERT INTO alertas(tipo,severidad,descripcion) VALUES (?,?,?)",input.get("tipo"),input.get("severidad"),input.get("descripcion"));return Map.of("status","created");}
  @PatchMapping("/api/alertas/{id}/close") Map<String,Object> closeAlert(@PathVariable UUID id){db.update("UPDATE alertas SET estado='cerrada', atendida_en=now() WHERE id=?",id);return Map.of("id",id,"estado","cerrada");}
  @GetMapping("/api/cameras") List<Map<String,Object>> cameras(){return db.queryForList("SELECT id,nombre,ubicacion,url_streaming AS \"urlStreaming\",anonimizado,activa FROM camaras WHERE activa=true");}
  @GetMapping("/api/cameras/{id}/stream") Map<String,Object> stream(@PathVariable UUID id){return db.query("SELECT url_streaming,anonimizado FROM camaras WHERE id=? AND activa=true",rs->{if(!rs.next())throw new ResponseStatusException(HttpStatus.NOT_FOUND,"Camara no disponible");return Map.of("camera_id",id,"stream_url",rs.getString(1),"anonimizado",rs.getBoolean(2));},id);}
  @GetMapping("/api/reportes/access-summary") Map<String,Object> accessReport(){return Map.of("type","access-summary","total",count("SELECT count(*) FROM accesos"),"generatedAt",Instant.now());}
  @GetMapping("/api/reportes/incident-summary") Map<String,Object> incidentReport(){return Map.of("type","incident-summary","active",count("SELECT count(*) FROM alertas WHERE estado <> 'cerrada'"),"generatedAt",Instant.now());}
  @PostMapping("/api/auth/register") @ResponseStatus(HttpStatus.CREATED) Map<String,Object> register(@Valid @RequestBody Register input){if(!input.consentimientoDatos())throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY,"Se requiere consentimiento informado");String role=input.role()==null?"residente":input.role();UUID roleId=db.queryForObject("SELECT id FROM roles WHERE nombre=?",UUID.class,role);if(roleId==null)throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Rol invalido");db.update("INSERT INTO usuarios(cedula,nombre_completo,correo,password_hash,role_id,consentimiento_datos,fecha_consentimiento) VALUES (?,?,?,?,?,true,now())",input.cedula(),input.nombreCompleto(),input.correo(),encoder.encode(input.password()),roleId);return Map.of("status","created","correo",input.correo());}
  @PostMapping("/api/auth/login") Map<String,Object> login(@Valid @RequestBody Login input){Map<String,Object> user=db.queryForMap("SELECT id,password_hash FROM usuarios WHERE correo=? AND activo=true",input.correo());if(!encoder.matches(input.password(),(String)user.get("password_hash")))throw new ResponseStatusException(HttpStatus.UNAUTHORIZED,"Credenciales invalidas");return Map.of("access_token",user.get("id").toString(),"token_type","bearer");}
  private long count(String sql){return db.queryForObject(sql,Long.class);}
}
