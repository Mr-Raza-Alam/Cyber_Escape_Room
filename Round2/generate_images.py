import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
    from PIL import Image, ImageDraw, ImageFont

def create_image(text, filename):
    try:
        font = ImageFont.truetype('consola.ttf', 20)
    except:
        font = ImageFont.load_default()
        
    lines = text.split('\n')
    width = max(len(line) for line in lines) * 14 + 100
    height = len(lines) * 25 + 60
    if width < 300: width = 300
    if height < 150: height = 150
    
    img = Image.new('RGB', (int(width), int(height)), color='#0d1117')
    d = ImageDraw.Draw(img)
    
    y = 30
    for line in lines:
        d.text((40, y), line, fill='#39ff14', font=font)
        y += 25
        
    img.save(filename)

snippets = {
    'c1': '#include <stdio.h>\nint bypass_firewall(int x) {\n    if (x % 2 = 0) return x << 1;\n    return x >> 1;\n}\nint mian() {\n    printf("%d", bypass_firewall(6));\n    return 0;\n}',
    'c2': '#include <stdio.h>\nvoid decrypt_node(int code) {\n    char base = \'A\'\n    printf("%c", base + (code % 26));\n}\nint main() {\n    decrypt_node[5];\n    return 0;\n}',
    'c3': '#include <stdio.h>\nvoid brute_force(char pwd()) {\n    for(int i = 0; i <= \'\\0\'; i++) {\n        pwd[i]--;\n    }\n}\nint main() {\n    char hash[] = "EBUB";\n    brute_force(hash);\n    printf("%s", hash);\n    return 0;\n}',
    'c4': '#include <stdio.h>\nint extract_payload(int arr[], int size) {\n    int sum = 0;\n    for (int i = 1; i < size, i + 2) {\n        sum += arr(i-1) * arr[i];\n    }\n    return sum;\n}\nint main() {\n    int buffer[] = {2, 3, 4, 1, 5, 2};\n    printf("%d", extract_payload(buffer, 6));\n    return 0;\n}',
    'c5': '#include <stdio.h>\nvoid inject_shellcode(char *src) {\n    char *ptr = src;\n    while (*ptr) {\n        if (*ptr >= \'a\' & *ptr <= \'z\') *ptr - 32;\n        ptr += 2;\n    }\n}\nint main() {\n    char target[] = "hacKeR";\n    inject_shellcode(target);\n    printf("%s", target);\n    return 0;\n}',
    'c6': '#include <stdio.h>\nint trace_route(int hops) {\n    if (hops = 0) return 0;\n    if (hops % 2 == 1) return 1 + trace_route(hops - 1);\n    return trace_route(hops / 2) + 2;\n}\nint main() {\n    printf("%d", trace_route{10});\n    return 0;\n}',
    'c7': '#include <stdio.h>\nvoid override_kernel() {\n    int a = 1. b = 1;\n    for (int i = 0; i < 3; i++) {\n        int a = i + 2;\n        b + a;\n    }\n    printf("%f", a + b);\n}\nint main() {\n    override_kernel();\n    return 0;\n}',
    'c8': '#include <stdio.h>\nvoid encrypt_packet(char *str) {\n    char *p1 = str;\n    char *p2 = tr;\n    while (*p2 != \'\\0\') p2++;\n    p2--;\n    while (p1 < p2) {\n        char temp = p1;\n        *p1 = *p2;\n        *p2 = temp;\n        p1++; p2--;\n    }\n}\nint main() {\n    char packet[] = "N01tCeR";\n    encrypt_packet(packet);\n    printf("%s" packet);\n    return 0;\n}',
    'c9': '#include <stdio.h>\nint intercept_handshake(int key) {\n    int auth = 0;\n    while(key > 0) {\n        auth += key % 10;\n        key /= 10;\n    }\n    return auth;\n}\nint main() {\n    print("%d", intercept_handshake(1024));\n    resturn 0;\n}',
    'c10': '#include <stdio.h>\nvoid overflow_buffer() {\n    int arr[] = {10, 20, 30, 40};\n    int res = 0;\n    for(int i=0, i<4; i++) {\n        res += arr[i];\n    }\n    printf("%d", res)\n}\nint main() {\n    overflow_buffer();\n    return 0;\n}',
    'c11': '#include <stdio.h>\nvoid corrupt_memory(char *mem) {\n    while(*mem) {\n        if(*mem == \'X\') {\n            *mem = \'Y\'\n        }\n        mem++;\n    }\n}\nint mian() {\n    char data[] = "AXBXCX";\n    corrupt_memory(data);\n    printf("%s", data);\n    return 0;\n}',
    'c12': '#include <stdio.h>\nint escalate_privilege(int level) {\n    if(level = 0) return 1;\n    return level * escalate_privilege(level - 1);\n}\nint main() {\n    printf("%d", escalate_privilege[4]);\n    return 0;\n}',
    'py1': 'def bypass_auth(token)\n    return token * 2 + token[:2]\n\nprint(bypass_auth("KEY"))',
    'py2': 'def parse_logs(logs):\n    return [p for p in log if p % 2 =! 0]\n\nprint(sum(parse_logs{[21, 22, 80, 443, 8080]}))',
    'py3': 'def map_network(ips)::\n    res = ""\n    fore ip in ips:\n        res + ip.split(".")(0)\n    return res\n\nprint(map_network(["192.168.1.1", "10.0.0.1"]))',
    'py4': 'def sql_inject(query):\n    parts = query.split()\n    payload = ""\n    for i, word in enumerate[parts]:\n        if i % 2 = 0:\n            payload += word(0)\n    print(payload)\n\nsql_inject("SELECT admin FROM users WHERE 1=1")',
    'py5': 'def extract_hash(data):\n    count = 0\n    for key, val in data.items():\n        if val > 5:\n            count += key\n        else\n            count -= val\n    return count\n\nprint(extract_hash({4: 6; 2: 3; 7: 10}))',
    'py6': 'def ping_sweep(subnet):\n    active == 0\n    while subnet > 0:\n        if subnet % 3 == 0:\n            active += 2\n        elif:\n            active -= 1\n        subnet - 2\n    return active\n\nprint(ping_sweep(10))',
    'py7': 'def decode_stream(st);\n    res = ""\n    for i in range(len[st]):\n        res += st[i-1;]\n    return res\n\nprint(decode_stream("CYBER"))',
    'py8': 'def print_payload(chars):\n    payload = ""\n    for i in range(len[chars]):\n        for j in range(i):\n            payload + chars[j]\n    print(Payload)\n\nPrint_payload("CODE")',
    'py9': 'def crack_hash(val):\n    res = 1\n    for i in range(1, val)\n        res *= i\n    return res\n\nprint(crack_hash(5))',
    'py10': 'def bypass_proxy(ips):\n    valid = []\n    for ip in ips\n        if len(ip) > 3:\n            valid.append(ip)\n    return len{valid}\n\nprint(bypass_proxy(["10.0", "192", "127.0.0"]))',
    'py11': 'def upload_trojan(size):\n    parts = 0\n    while size > 0\n        parts + 1\n        size -= 10\n    print(Parts)\n\nupload_Trojan(50)',
    'py12': 'def sniff_packets(data):\n    return [d for d in data if d = \'A\']\n\nprint(len(sniff_packets([\'A\', \'B\', \'A\', \'C\'])))'
}

os.makedirs('static/images', exist_ok=True)
for qid, code in snippets.items():
    create_image(code, f'static/images/{qid}.png')
    
print("Generated 24 code snippet images securely!")
