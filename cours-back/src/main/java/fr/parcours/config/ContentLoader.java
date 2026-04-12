package fr.parcours.config;

import fr.parcours.service.ContentManagerService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class ContentLoader implements ApplicationRunner {

    private final ContentManagerService contentManagerService;

    @Override
    public void run(ApplicationArguments args) {
        log.info("🔄 Chargement du contenu YAML...");
        contentManagerService.loadAll();
        log.info("✅ Contenu chargé: {} sujets, {} étapes",
            contentManagerService.getSubjects().size(),
            contentManagerService.getAllSteps().size());
    }
}
