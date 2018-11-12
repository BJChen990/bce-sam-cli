package helloworld;

import com.baidubce.faas.core.FaasContext;
import com.baidubce.faas.core.InvokeHandler;

import java.io.InputStream;
import java.io.OutputStream;

public class Index implements InvokeHandler
{
    public void invoke(InputStream input, OutputStream output, FaasContext context) throws Exception {
        System.out.println("console outlog");
        System.err.println("console errlog");
        output.write("hello world!".getBytes());
    }
}