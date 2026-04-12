package fr.parcours.model.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "subjectprogress")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SubjectProgress {

    @Id
    @Column(name = "id", nullable = false)
    private String id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "subject_id", nullable = false)
    private String subjectId;

    @Column(name = "score")
    @Builder.Default
    private int score = 0;
}
