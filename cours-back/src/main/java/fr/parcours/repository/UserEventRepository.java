package fr.parcours.repository;

import fr.parcours.model.entity.UserEvent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface UserEventRepository extends JpaRepository<UserEvent, String> {
    Optional<UserEvent> findByUserIdAndEventId(String userId, String eventId);
    boolean existsByUserIdAndEventId(String userId, String eventId);
}
