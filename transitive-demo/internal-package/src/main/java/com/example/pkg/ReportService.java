package com.example.pkg;

import com.example.utils.XmlHelper;
import com.example.utils.ConfigLoader;

import java.util.Map;

public class ReportService {

    private final XmlHelper xmlHelper = new XmlHelper();
    private final ConfigLoader configLoader = new ConfigLoader();

    public String exportToXml(Object data) {
        return xmlHelper.toXml(data);
    }

    public Object importFromXml(String xml) {
        return xmlHelper.fromXml(xml);
    }

    public Map<String, Object> loadConfig(String yaml) {
        return configLoader.load(yaml);
    }
}