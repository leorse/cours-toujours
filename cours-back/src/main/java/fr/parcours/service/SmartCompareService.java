package fr.parcours.service;

import org.springframework.stereotype.Service;
import java.util.*;
import java.util.regex.Pattern;

@Service
public class SmartCompareService {

    private static final double TOLERANCE = 0.0001;
    private static final Pattern FRACTION = Pattern.compile("^(-?\\d+)\\s*/\\s*(-?\\d+)$");

    public boolean compare(Object userAnswer, Object expected) {
        if (userAnswer == null || expected == null) return false;

        if (expected instanceof List<?> expectedList) {
            List<String> exp = toStringList(expectedList);
            List<String> usr = toStringList(toList(userAnswer));
            return listsEqual(usr, exp);
        }

        String expStr = expected.toString().trim();
        String usrStr = userAnswer.toString().trim();

        Double expNum = parseFraction(expStr);
        Double usrNum = parseFraction(usrStr);

        try {
            double ev = expNum != null ? expNum : Double.parseDouble(expStr);
            double uv = usrNum != null ? usrNum : Double.parseDouble(usrStr);
            return Math.abs(ev - uv) < TOLERANCE;
        } catch (NumberFormatException ignored) {}

        return expStr.equalsIgnoreCase(usrStr);
    }

    public boolean listsEqual(List<String> user, List<String> expected) {
        if (user.size() != expected.size()) return false;
        for (int i = 0; i < expected.size(); i++) {
            if (!expected.get(i).trim().equalsIgnoreCase(user.get(i).trim())) return false;
        }
        return true;
    }

    private Double parseFraction(String s) {
        var m = FRACTION.matcher(s.trim());
        if (m.matches()) {
            double den = Double.parseDouble(m.group(2));
            if (den == 0) return null;
            return Double.parseDouble(m.group(1)) / den;
        }
        return null;
    }

    private List<String> toStringList(List<?> list) {
        return list.stream().map(o -> o == null ? "" : o.toString()).toList();
    }

    private List<?> toList(Object obj) {
        if (obj instanceof List<?> l) return l;
        return List.of(obj.toString());
    }
}
