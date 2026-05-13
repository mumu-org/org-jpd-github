package com.example.utils;

import org.yaml.snakeyaml.Yaml;

import java.util.Map;

public class ConfigLoader {

    public Map<String, Object> load(String yamlContent) {
        Yaml yaml = new Yaml();
        // CVE-2022-1471: 使用无限制的 Constructor，可导致反序列化攻击
        return yaml.load(yamlContent);
    }
}
