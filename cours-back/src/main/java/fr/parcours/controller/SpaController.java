package fr.parcours.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

/**
 * Redirige toutes les routes non-API et non-statiques vers index.html
 * pour que React Router (SPA) puisse gérer le routage côté client.
 */
@Controller
public class SpaController {

    @RequestMapping(value = { "/", "/{path:[^\\.]*}", "/**/{path:[^\\.]*}" })
    public String spa() {
        return "forward:/index.html";
    }
}
