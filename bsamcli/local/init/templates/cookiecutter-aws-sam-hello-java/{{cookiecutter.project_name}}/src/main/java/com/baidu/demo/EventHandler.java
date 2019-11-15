package com.baidu.demo;

import com.baidubce.cfc.core.CfcContext;
import com.baidubce.cfc.core.RequestHandler;
import com.baidubce.cfc.core.StsCredential;

import java.util.logging.Logger;

public class EventHandler implements RequestHandler<UserInfo, String> {
    Logger logger = Logger.getLogger("java.util.logging.ConsoleHandler");

    public EventHandler() {
    }

    @Override
    public String handler(UserInfo user, CfcContext context) throws Exception {
        return "Hello, " + user.getFirstName() + " " + user.getLastName();
    }
}
