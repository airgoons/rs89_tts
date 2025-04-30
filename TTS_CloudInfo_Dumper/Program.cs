using System;
using System.IO;

using SteamCloudFileManager;

namespace TTS_GetCloudInfo_BSON {
    internal class Program {
        static void Main(string[] args) {
            uint tts_app_id = 286160;

            var remoteStorage = new RemoteStorage(tts_app_id);
            IRemoteFile cloudinfo_bson = remoteStorage.GetFile("CloudInfo.bson");
            File.WriteAllBytes(cloudinfo_bson.Name, cloudinfo_bson.ReadAllBytes());

            Console.WriteLine("done");
        }
    }
}
