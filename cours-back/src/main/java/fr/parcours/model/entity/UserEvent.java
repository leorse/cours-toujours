package fr.parcours.model.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "userevent")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserEvent {

    @Id
    @Column(name = "id", nullable = false)
    private String id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "event_id", nullable = false)
    private String eventId;

    @Column(name = "timestamp")
    private LocalDateTime timestamp;
}
