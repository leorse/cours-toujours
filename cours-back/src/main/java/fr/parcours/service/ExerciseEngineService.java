package fr.parcours.service;

import fr.parcours.model.content.ExerciseTemplate;
import fr.parcours.model.dto.GeneratedExercise;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
@RequiredArgsConstructor
@Slf4j
public class ExerciseEngineService {

    private static final Pattern EXPR = Pattern.compile("\\[\\[(.+?)]]");
    private static final Pattern VAR  = Pattern.compile("\\{(\\w+)}");

    public Optional<GeneratedExercise> generateExercise(ExerciseTemplate template) {
        try {
            Map<String, Object> vars = generateVariables(template.getVars());
            Map<String, Object> content = template.getContent() != null ? template.getContent() : Map.of();

            GeneratedExercise ex = new GeneratedExercise();
            ex.setId(UUID.randomUUID().toString());
            ex.setTemplateId(template.getId());
            ex.setType(template.getType() != null ? template.getType() : template.getInteraction());
            ex.setRenderType(template.getRenderType());
            ex.setMultiple(template.isMultiple());
            ex.setTags(template.getTags());
            ex.setVariables(vars);
            ex.setQuestion(interpolate((String) content.get("question"), vars));
            ex.setExplanation(interpolate((String) content.get("explanation"), vars));
            ex.setUnit(interpolate((String) content.get("unit"), vars));

            Object optRaw = content.get("options");
            if (optRaw instanceof List<?> opts) {
                ex.setOptions(opts.stream().map(o -> interpolate(o.toString(), vars)).toList());
            }

            Object answer;
            if (template.getLogic() != null && !template.getLogic().isBlank()) {
                answer = fmt(evalLogic(template.getLogic(), vars));
            } else {
                Object raw = content.get("answer");
                if (raw instanceof List<?> ansList) {
                    answer = ansList.stream().map(a -> interpolate(a.toString(), vars)).toList();
                } else {
                    answer = interpolate(raw != null ? raw.toString() : "", vars);
                }
            }
            ex.setAnswer(answer);
            return Optional.of(ex);
        } catch (Exception e) {
            log.debug("Erreur génération {}: {}", template.getId(), e.getMessage());
            return Optional.empty();
        }
    }

    public List<GeneratedExercise> generateExercises(List<ExerciseTemplate> templates, int count) {
        if (templates.isEmpty()) return List.of();
        List<GeneratedExercise> result = new ArrayList<>();
        Random rng = new Random();
        int attempts = 0;
        while (result.size() < count && attempts < count * 3) {
            generateExercise(templates.get(rng.nextInt(templates.size()))).ifPresent(result::add);
            attempts++;
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> generateVariables(Map<String, Object> defs) {
        Map<String, Object> vars = new HashMap<>();
        if (defs == null) return vars;
        Random rng = new Random();
        for (var e : defs.entrySet()) {
            Object def = e.getValue();
            if (def instanceof List<?> choices) {
                vars.put(e.getKey(), choices.get(rng.nextInt(choices.size())));
            } else if (def instanceof Map<?, ?> range) {
                var r = (Map<String, Object>) range;
                int min = toInt(r.getOrDefault("min", 0));
                int max = toInt(r.getOrDefault("max", 10));
                vars.put(e.getKey(), min + rng.nextInt(Math.max(1, max - min + 1)));
            } else {
                vars.put(e.getKey(), def);
            }
        }
        return vars;
    }

    private String interpolate(String text, Map<String, Object> vars) {
        if (text == null) return null;
        // Évaluer [[expr]]
        Matcher em = EXPR.matcher(text);
        StringBuffer sb = new StringBuffer();
        while (em.find()) {
            String expr = replaceVars(em.group(1), vars);
            Object res = safeEval(expr);
            em.appendReplacement(sb, Matcher.quoteReplacement(fmt(res)));
        }
        em.appendTail(sb);
        return replaceVars(sb.toString(), vars);
    }

    private String replaceVars(String text, Map<String, Object> vars) {
        Matcher m = VAR.matcher(text);
        StringBuffer sb = new StringBuffer();
        while (m.find()) {
            Object val = vars.getOrDefault(m.group(1), "{" + m.group(1) + "}");
            m.appendReplacement(sb, Matcher.quoteReplacement(fmt(val)));
        }
        m.appendTail(sb);
        return sb.toString();
    }

    private Object evalLogic(String logic, Map<String, Object> vars) {
        return safeEval(replaceVars(logic, vars));
    }

    private Object safeEval(String expr) {
        // Évaluation arithmétique simple
        try {
            return evalArith(expr.trim());
        } catch (Exception e) {
            return expr;
        }
    }

    private double evalArith(String expr) {
        // Support basique: +, -, *, /
        expr = expr.trim();
        // Chercher + ou - (hors parenthèses)
        int depth = 0;
        for (int i = expr.length() - 1; i >= 0; i--) {
            char c = expr.charAt(i);
            if (c == ')') depth++;
            if (c == '(') depth--;
            if (depth == 0 && (c == '+' || c == '-') && i > 0) {
                double left = evalArith(expr.substring(0, i));
                double right = evalArith(expr.substring(i + 1));
                return c == '+' ? left + right : left - right;
            }
        }
        // Chercher * ou /
        for (int i = expr.length() - 1; i >= 0; i--) {
            char c = expr.charAt(i);
            if (c == ')') depth++;
            if (c == '(') depth--;
            if (depth == 0 && (c == '*' || c == '/')) {
                double left = evalArith(expr.substring(0, i));
                double right = evalArith(expr.substring(i + 1));
                return c == '*' ? left * right : left / right;
            }
        }
        if (expr.startsWith("(") && expr.endsWith(")")) return evalArith(expr.substring(1, expr.length() - 1));
        return Double.parseDouble(expr);
    }

    private String fmt(Object val) {
        if (val instanceof Double d && d == Math.floor(d) && !Double.isInfinite(d)) return String.valueOf(d.longValue());
        if (val instanceof Long l) return String.valueOf(l);
        if (val instanceof Integer i) return String.valueOf(i);
        return val != null ? val.toString() : "";
    }

    private int toInt(Object v) {
        if (v instanceof Integer i) return i;
        if (v instanceof Long l) return l.intValue();
        if (v instanceof Double d) return d.intValue();
        try { return Integer.parseInt(v.toString()); } catch (Exception e) { return 0; }
    }
}
