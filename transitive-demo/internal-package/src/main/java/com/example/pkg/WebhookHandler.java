package com.example.pkg;

import com.example.utils.XmlHelper;

public class WebhookHandler {

    private final XmlHelper xmlHelper = new XmlHelper();

    public Object processPayload(String xmlPayload) {
        return xmlHelper.fromXml(xmlPayload);
    }
}