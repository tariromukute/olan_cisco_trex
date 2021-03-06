# Example for create a delay in the client side ( the request is splited to 2)
# send 10 bytes (http_req[:10])
# wait 
# send 10 bytes (http_req[10:])



from trex.astf.api import *


# we can send either Python bytes type as below:
http_req = b'GET /3384 HTTP/1.1\r\nHost: 22.0.0.3\r\nConnection: Keep-Alive\r\nUser-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)\r\nAccept: */*\r\nAccept-Language: en-us\r\nAccept-Encoding: gzip, deflate, compress\r\n\r\n'
# or we can send Python string containing ascii chars, as below:
http_response = 'HTTP/1.1 200 OK\r\nServer: Microsoft-IIS/6.0\r\nContent-Type: text/html\r\nContent-Length: 32000\r\n\r\n<html><pre>**********</pre></html>'


class Prof1():
    def __init__(self):
        pass  # tunables

    def _tcp450b(self,**kwargs):
        http_req = 'GET /450 HTTP/1.1\r\nHost: 10.10.1.1\r\nConnection: close\r\nUser-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 8.0\r\nAccept: */*\r\nAccept-Language: en-us\r\nAccept-Encoding: gzip, deflate, compress\r\n\r\n'
        # or we can send Python string containing ascii chars, as below:
        http_response = 'HTTP/1.1 200 OK\r\nServer: Jetty/4.2.9rc2 (SunOS/5.8 sparc java/1.4.1_04)\r\nContent-Type: text/html\r\nConnection: close\r\nContent-Length: 11100\r\n\r\n'
        http_response2 = 11076 * '*'
        http_total_response = http_response + '<html><pre>' + http_response2 + '</pre></html>'
        # client commands
        prog_c = ASTFProgram()
        prog_c.connect();
        prog_c.send(http_req)
        prog_c.recv(len(http_total_response))
        prog_c.delay(10)
        # server commands
        prog_s = ASTFProgram()
        prog_s.recv(len(http_req))
        prog_s.delay(10);
        prog_s.send(http_total_response)
        prog_s.wait_for_peer_close()

        info = ASTFGlobalInfo()
        info.tcp.mss = 1100
        info.tcp.rxbufsize = 32768
        info.tcp.txbufsize = 32768
        info.tcp.initwnd = 2
        info.tcp.do_rfc1323 = 0
        info.tcp.no_delay = 1
        info.scheduler.rampup_sec = 30
        return {'prog_c':prog_c,'prog_s':prog_s,'info':info}

    def create_profile(self):
        # client commands
        d = self._tcp450b()

        # ip generator
        ip_gen_c = ASTFIPGenDist(ip_range=["16.0.0.0", "16.0.0.255"], distribution="seq")
        ip_gen_s = ASTFIPGenDist(ip_range=["48.0.0.0", "48.0.255.255"], distribution="seq")
        ip_gen = ASTFIPGen(glob=ASTFIPGenGlobal(ip_offset="1.0.0.0"),
                           dist_client=ip_gen_c,
                           dist_server=ip_gen_s)

        # template
        temp_c = ASTFTCPClientTemplate(program=d['prog_c'], ip_gen=ip_gen)
        temp_s = ASTFTCPServerTemplate(program=d['prog_s'])  # using default association
        template = ASTFTemplate(client_template=temp_c, server_template=temp_s)

        # profile
        profile = ASTFProfile(default_c_glob_info=d['info'], default_ip_gen=ip_gen, templates=template)
        return profile

    def get_profile(self,**kwargs):
        return self.create_profile()


def register():
    return Prof1()
