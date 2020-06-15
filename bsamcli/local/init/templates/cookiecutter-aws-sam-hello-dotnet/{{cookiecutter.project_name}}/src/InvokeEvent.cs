using Newtonsoft.Json;
namespace BaiduBce.CFC.Demo {
    public class InvokeEvent {
        [JsonProperty(PropertyName = "event")]
        public string Event { get; set; }        
    }
}
