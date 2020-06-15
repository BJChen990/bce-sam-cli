using System;
using System.IO;
using Newtonsoft.Json;
using BaiduBce.CFC.Core;

namespace BaiduBce.CFC.Demo
{
    public class StreamHandlerDemo : StreamHandler
    {
        public void Handler(Stream input, Stream output, InvokeContext context)
        {
            StreamReader reader = new StreamReader(input);
            InvokeEvent invoke = JsonConvert.DeserializeObject<InvokeEvent>(reader.ReadToEnd());
            StreamWriter writer = new StreamWriter(output);
            writer.AutoFlush = true;

            if (invoke.Event != null)
            {
                Console.Out.Write(invoke.Event);
            }
            
            Console.Out.WriteLine("RequestID = {0}", context.RequestID);
            Console.Out.WriteLine("FunctionBrn = {0}", context.FunctionBrn);

            writer.WriteLine("Hello world!");
        }
    }
}
