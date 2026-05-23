package com.example.utils;

import com.thoughtworks.xstream.XStream;

public class XmlHelper {

    private final XStream xstream;

    public XmlHelper() {
        this.xstream = new XStream();
        // 注意：这里没有调用 setupDefaultSecurity，是漏洞触发点
    }

    public String toXml(Object obj) {
        return xstream.toXML(obj);
    }

    public Object fromXml(String xml) {
        // CVE-2021-21344: 反序列化任意类，可导致 RCE
        return xstream.fromXML(xml);
    }
}
