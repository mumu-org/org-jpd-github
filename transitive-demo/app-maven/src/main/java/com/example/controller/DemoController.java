package com.example;

import com.example.pkg.ReportService;
import com.example.pkg.WebhookHandler;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
public class DemoController {

    private final ReportService reportService = new ReportService();
    private final WebhookHandler webhookHandler = new WebhookHandler();

    @PostMapping("/report/export")
    public String exportReport(@RequestBody Map<String, Object> data) {
        return reportService.exportToXml(data);
    }

    @PostMapping("/report/import")
    public Object importReport(@RequestBody String xml) {
        // 调用链: DemoController → ReportService → XmlHelper → XStream → 漏洞
        return reportService.importFromXml(xml);
    }

    @PostMapping("/webhook")
    public Object handleWebhook(@RequestBody String xmlPayload) {
        // 调用链: DemoController → WebhookHandler → XmlHelper → XStream → 漏洞
        return webhookHandler.processPayload(xmlPayload);
    }

    @PostMapping("/config")
    public Object loadConfig(@RequestBody String yaml) {
        // 调用链: DemoController → ReportService → ConfigLoader → Yaml.load → 漏洞
        return reportService.loadConfig(yaml);
    }
}