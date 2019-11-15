package com.baidu.demo;

import com.baidubce.cfc.core.CfcContext;
import com.baidubce.cfc.core.StreamHandler;

import java.io.InputStream;
import java.io.OutputStream;

public class SimpleHandler implements StreamHandler {

    @Override
    public void handler(InputStream input, OutputStream output, CfcContext context) throws Exception {        
        output.write("hello world!".getBytes());
    }
}
