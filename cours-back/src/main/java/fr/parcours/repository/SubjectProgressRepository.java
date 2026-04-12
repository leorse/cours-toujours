package fr.parcours.repository;

import fr.parcours.model.entity.SubjectProgress;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface SubjectProgressRepository extends JpaRepository<SubjectProgress, String> {
    List<SubjectProgress> findByUserId(String userId);
    Optional<SubjectProgress> findByUserIdAndSubjectId(String userId, String subjectId);
}
