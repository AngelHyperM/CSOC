def format_text(text):
    unique_ips = text.split('\n')
    unique_ips = list(set(unique_ips))
    unique_ips = "\n".join(unique_ips)
    text = text.replace('.', '[.]').replace('@', '[@]').replace(' ', '')
    unique_ips = unique_ips.replace('.', '[.]').replace('@', '[@]').replace(' ', '')
    return text, unique_ips

def obtener_texto():
    print("Text:")
    text = ""
    while True:
        linea = input()
        if linea:
            text += linea + "\n"
        else:
            break
    #clearConsole()
    return text

texto = obtener_texto()
format_text(texto)