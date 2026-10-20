import unicodedata
import urllib.parse

import flet as ft

# ----------------------------------------------------------------------
# CONFIGURAÇÕES DO SALVADOR LANCHES  (se precisar trocar algo, é aqui)
# ----------------------------------------------------------------------
NUMERO_WHATSAPP_SALVADOR = "5519989963063"  # 55 + DDD + número, só dígitos
CHAVE_PIX_SALVADOR = "19995153349"  # CONFIRA se é a chave real
NOME_PIX = "SALVADOR LANCHES"  # nome que aparece no banco (até 25 letras)
CIDADE_PIX = "SANTA BÁRBARA DOESTE"  # cidade do carrinho, sem acento (até 15 letras)


# ----------------------------------------------------------------------
# PIX COPIA E COLA (o cliente cola no app do banco e o valor já vem certo)
# ----------------------------------------------------------------------
def _ascii(texto):
  sem_acento = unicodedata.normalize("NFKD", texto)
  return sem_acento.encode("ascii", "ignore").decode("ascii")


def _campo_pix(identificador, valor):
  return f"{identificador}{len(valor):02d}{valor}"


def _crc16_pix(texto):
  crc = 0xFFFF
  for byte in texto.encode("ascii"):
    crc ^= byte << 8
    for _ in range(8):
      crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
      crc &= 0xFFFF
  return f"{crc:04X}"


def gerar_pix_copia_e_cola(chave, valor, nome, cidade):
  conta = _campo_pix("00", "br.gov.bcb.pix") + _campo_pix("01", chave)
  payload = (
      _campo_pix("00", "01")
      + _campo_pix("01", "11")
      + _campo_pix("26", conta)
      + _campo_pix("52", "0000")
      + _campo_pix("53", "986")
      + _campo_pix("54", f"{valor:.2f}")
      + _campo_pix("58", "BR")
      + _campo_pix("59", _ascii(nome)[:25])
      + _campo_pix("60", _ascii(cidade)[:15])
      + _campo_pix("62", _campo_pix("05", "***"))
      + "6304"
  )
  return payload + _crc16_pix(payload)


async def main(page: ft.Page):
  page.title = "SALVADOR LANCHES - CLIENTE"
  page.theme_mode = ft.ThemeMode.DARK
  page.bgcolor = "#0B0C10"
  page.scroll = ft.ScrollMode.AUTO

  # Cores Neon
  CYAN = "#00FFFF"
  PURPLE = "#9D00FF"
  GREEN = "#39FF14"
  YELLOW = "#FFD700"

  # Imagens (a foto do Salvador fica na pasta "assets")
  FOTO_SALVADOR = "/salvador.png"
  FOTO_LANCHE_ILUSTRATIVA = "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=150&auto=format&fit=crop&q=80"

  # Carrinho de compras do cliente
  carrinho = []

  # Variáveis temporárias de estado
  lanche_atual = None
  quantidade_atual = 1
  ingredientes_removidos = []
  adicionais_escolhidos = []
  forma_pagamento_selecionada = "PIX"

  # Componentes de UI
  lista_revisao_ui = ft.Column(spacing=5)
  total_revisao_ui = ft.Text(
      "", size=18, color=YELLOW, weight=ft.FontWeight.BOLD
  )

  txt_nome_player = ft.TextField(
      label="SEU NOME (CLIENTE)",
      border_color=CYAN,
      focused_border_color=GREEN,
      text_style=ft.TextStyle(color="#FFFFFF"),
  )

  cardapio = [
      {
          "id": "01",
          "nome": "MISTO QUENTE",
          "preco": 20.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "2 Presunto",
              "2 queijo",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
      {
          "id": "02",
          "nome": "X-BURGER",
          "preco": 22.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "Hambúrguer",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
      {
          "id": "03",
          "nome": "X-SALADA",
          "preco": 23.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "Hambúrguer",
              "presunto",
              "queijo",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
      {
          "id": "04",
          "nome": "X-MILHO",
          "preco": 23.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "Hambúrguer",
              "milho",
              "presunto",
              "queijo",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
      {
          "id": "05",
          "nome": "X-EGG",
          "preco": 24.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "Hambúrguer",
              "ovo",
              "presunto",
              "queijo",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
      {
          "id": "06",
          "nome": "X-CALABRESA",
          "preco": 24.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "Calabresa",
              "ovo",
              "presunto",
              "queijo",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
      {
          "id": "07",
          "nome": "X-FRANGO",
          "preco": 27.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "Frango",
              "ovo",
              "presunto",
              "queijo",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
      {
          "id": "08",
          "nome": "X-BACON",
          "preco": 28.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "Hambúrguer",
              "bacon",
              "ovo",
              "presunto",
              "queijo",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
      {
          "id": "09",
          "nome": "X-EGG ESPECIAL",
          "preco": 29.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "2 Hambúrguer",
              "2 presunto",
              "2 queijo",
              "2 ovo",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
      {
          "id": "10",
          "nome": "FRANBACON",
          "preco": 30.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "Frango",
              "bacon",
              "ovo",
              "presunto",
              "queijo",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
      {
          "id": "11",
          "nome": "X-TUDO",
          "preco": 36.00,
          "imagem": FOTO_LANCHE_ILUSTRATIVA,
          "ingredientes": [
              "Hambúrguer",
              "salsicha",
              "bacon",
              "frango",
              "calabresa",
              "ovo",
              "presunto",
              "queijo",
              "milho",
              "alface",
              "tomate",
              "maionese",
              "mostarda",
              "ketchup",
          ],
      },
  ]

  # Adicionais
  tabela_adicionais = [
      {"nome": "Milho", "preco": 1.00},
      {"nome": "Ovo", "preco": 1.00},
      {"nome": "Salsicha", "preco": 2.00},
      {"nome": "Hambúrguer", "preco": 4.00},
      {"nome": "Bacon", "preco": 4.00},
      {"nome": "Calabresa", "preco": 4.00},
      {"nome": "Presunto e Queijo", "preco": 4.00},
      {"nome": "Frango", "preco": 5.00},
      {"nome": "Catupiry", "preco": 5.00},
  ]

  # --- CUSTOMIZAÇÃO ---
  img_modal_lanche = ft.Image(
      src="", width=60, height=60, border_radius=8, fit="cover"
  )

  def abrir_customizacao(lanche_selecionado):
    nonlocal lanche_atual, quantidade_atual, ingredientes_removidos, adicionais_escolhidos
    lanche_atual = lanche_selecionado
    quantidade_atual = 1
    ingredientes_removidos = []
    adicionais_escolhidos = []

    txt_quantidade.value = str(quantidade_atual)
    img_modal_lanche.src = lanche_atual["imagem"]

    comp_ingredientes.controls.clear()
    for ing in lanche_atual["ingredientes"]:
      comp_ingredientes.controls.append(
          ft.Checkbox(
              label=ing.capitalize(),
              value=True,
              label_style=ft.TextStyle(color="#FFFFFF"),
              active_color=PURPLE,
              on_change=lambda e, i=ing: gerenciar_ingredientes(e, i),
          )
      )

    comp_adicionais.controls.clear()
    for adc in tabela_adicionais:
      comp_adicionais.controls.append(
          ft.Checkbox(
              label=f"{adc['nome']} (+R$ {adc['preco']:.2f})",
              value=False,
              label_style=ft.TextStyle(color="#FFFFFF"),
              active_color=GREEN,
              on_change=lambda e, a=adc: gerenciar_adicionais(e, a),
          )
      )

    modal_customizar.title = ft.Row([
        img_modal_lanche,
        ft.Text(
            f"⚙️ {lanche_atual['nome']}",
            color=CYAN,
            weight=ft.FontWeight.BOLD,
            size=16,
        ),
    ])
    page.show_dialog(modal_customizar)

  def gerenciar_ingredientes(e, ingrediente):
    if not e.control.value:
      ingredientes_removidos.append(ingrediente)
    else:
      if ingrediente in ingredientes_removidos:
        ingredientes_removidos.remove(ingrediente)

  def gerenciar_adicionais(e, adicional):
    if e.control.value:
      adicionais_escolhidos.append(adicional)
    else:
      if adicional in adicionais_escolhidos:
        adicionais_escolhidos.remove(adicional)

  def Blacksmith_alterar_qtd(fator):
    nonlocal quantidade_atual
    quantidade_atual += fator
    if quantidade_atual < 1:
      quantidade_atual = 1
    txt_quantidade.value = str(quantidade_atual)
    page.update()

  def confirmar_e_adicionar_ao_carrinho(e):
    preco_adicionais = sum(item["preco"] for item in adicionais_escolhidos)
    preco_final_unitario = lanche_atual["preco"] + preco_adicionais

    carrinho.append({
        "nome": lanche_atual["nome"],
        "quantidade": quantidade_atual,
        "preco_unitario": preco_final_unitario,
        "preco_total": preco_final_unitario * quantidade_atual,
        "sem": list(ingredientes_removidos),
        "com": [item["nome"] for item in adicionais_escolhidos],
    })

    page.pop_dialog()
    btn_ver_pedido.content = ft.Text(
        f"🛒 VER MEU PEDIDO ({len(carrinho)} ITEM/NS)",
        color="#0B0C10",
        weight=ft.FontWeight.BOLD,
    )
    btn_ver_pedido.visible = True
    page.update()

  txt_quantidade = ft.Text(
      "1", size=22, color="#FFFFFF", weight=ft.FontWeight.BOLD
  )
  comp_ingredientes = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)
  comp_adicionais = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)

  modal_customizar = ft.AlertDialog(
      modal=True,
      bgcolor="#1F2833",
      content=ft.Container(
          width=400,
          content=ft.Column(
              [
                  ft.Text(
                      "🔢 QUANTIDADE:",
                      color=YELLOW,
                      size=14,
                      weight=ft.FontWeight.BOLD,
                  ),
                  ft.Row(
                      [
                          ft.IconButton(
                              icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
                              icon_color=PURPLE,
                              icon_size=32,
                              on_click=lambda e: Blacksmith_alterar_qtd(-1),
                          ),
                          ft.Container(
                              content=txt_quantidade,
                              padding=10,
                              bgcolor="#0B0C10",
                              border_radius=5,
                          ),
                          ft.IconButton(
                              icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                              icon_color=GREEN,
                              icon_size=32,
                              on_click=lambda e: Blacksmith_alterar_qtd(1),
                          ),
                      ],
                      alignment=ft.MainAxisAlignment.CENTER,
                  ),
                  ft.Divider(color=PURPLE),
                  ft.Text(
                      "❌ RETIRAR INGREDIENTES (Desmarque para remover):",
                      color=YELLOW,
                      size=12,
                      weight=ft.FontWeight.BOLD,
                  ),
                  ft.Container(content=comp_ingredientes, height=120),
                  ft.Divider(color=PURPLE),
                  ft.Text(
                      "⚡ TURBINAR LANCHE (Adicionais):",
                      color=GREEN,
                      size=12,
                      weight=ft.FontWeight.BOLD,
                  ),
                  ft.Container(content=comp_adicionais, height=120),
              ],
              tight=True,
          ),
      ),
      actions=[
          ft.Button(
              content=ft.Text(
                  "CONFIRMAR ITEM ⚔️",
                  color="#0B0C10",
                  weight=ft.FontWeight.BOLD,
              ),
              bgcolor=GREEN,
              elevation=2,
              on_click=confirmar_e_adicionar_ao_carrinho,
          ),
          ft.TextButton("CANCELAR", on_click=lambda e: page.pop_dialog()),
      ],
  )

  # --- PIX (copia e cola) ---
  codigo_pix_atual = ""
  codigo_pix_ui = ft.Text(
      "", size=11, color="#FFFFFF", selectable=True, text_align=ft.TextAlign.CENTER
  )
  valor_pix_text = ft.Text(
      "", size=20, color=GREEN, weight=ft.FontWeight.BOLD
  )
  aviso_copia_ui = ft.Text(
      "", size=12, color=GREEN, weight=ft.FontWeight.BOLD
  )

  async def copiar_codigo_pix(e):
    try:
      await ft.Clipboard().set(codigo_pix_atual)
      aviso_copia_ui.value = "✅ Código copiado! Cole no app do seu banco."
    except Exception:
      aviso_copia_ui.value = "Não consegui copiar. Segure o código e copie."
    page.update()

  # --- ENVIO DO WHATSAPP ---
  modal_final = ft.AlertDialog(modal=True, bgcolor="#1F2833")

  def pedido_enviado(e):
    carrinho.clear()
    btn_ver_pedido.visible = False
    page.pop_dialog()
    page.update()

  def finalizar_pedido(tipo_pagamento):
    nome_cliente = txt_nome_player.value.strip().upper()
    total_geral = sum(item["preco_total"] for item in carrinho)

    msg = f"🍔 *NOVO PEDIDO - SALVADOR LANCHES*\n"
    msg += f"👤 *Cliente:* {nome_cliente}\n"
    msg += f"-----------------------------------\n"

    for item in carrinho:
      msg += f"• *{item['quantidade']}x {item['nome']}* - R$ {item['preco_total']:.2f}\n"
      if item["sem"]:
        msg += f"   ❌ Sem: {', '.join(item['sem'])}\n"
      if item["com"]:
        msg += f"   🟢 Com: {', '.join(item['com'])}\n"

    msg += f"-----------------------------------\n"
    msg += f"💰 *TOTAL:* R$ {total_geral:.2f}\n"
    msg += f"📱 *Forma de Pagamento:* {tipo_pagamento}\n\n"

    if tipo_pagamento == "PIX":
      msg += "📌 *Vou enviar o comprovante do PIX logo em seguida!*"
    else:
      msg += "📌 *Pagamento será realizado no momento da retirada!*"

    link_whatsapp = (
        f"https://wa.me/{NUMERO_WHATSAPP_SALVADOR}"
        f"?text={urllib.parse.quote(msg)}"
    )

    texto_instrucao = (
        "Depois de enviar, mande também o comprovante do PIX na conversa!"
        if tipo_pagamento == "PIX"
        else "Aguarde a confirmação do seu pedido pelo WhatsApp!"
    )

    modal_final.title = ft.Text(
        "📲 ÚLTIMO PASSO!", color=YELLOW, weight=ft.FontWeight.BOLD
    )
    modal_final.content = ft.Container(
        width=400,
        content=ft.Column(
            [
                ft.Text(
                    "Seu pedido ainda NÃO foi enviado. Toque no botão verde:"
                    " o WhatsApp abre com tudo pronto e você só aperta"
                    " ENVIAR.",
                    color="#FFFFFF",
                    size=13,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Button(
                    content=ft.Text(
                        "ABRIR WHATSAPP E ENVIAR 📲",
                        color="#0B0C10",
                        weight=ft.FontWeight.BOLD,
                    ),
                    bgcolor=GREEN,
                    elevation=2,
                    url=link_whatsapp,
                ),
                ft.Text(
                    f"Cliente: {nome_cliente}",
                    color=CYAN,
                    size=15,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text("Tempo estimado de preparo:", color="#FFFFFF", size=13),
                ft.Container(
                    content=ft.Text(
                        "⏱️ 15 A 25 MINUTOS",
                        color="#0B0C10",
                        weight=ft.FontWeight.BOLD,
                        size=16,
                    ),
                    bgcolor=GREEN,
                    padding=10,
                    border_radius=5,
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.NOTIFICATIONS_ACTIVE,
                                        color=CYAN,
                                        size=22,
                                    ),
                                    ft.Text(
                                        "AVISO IMPORTANTE",
                                        color=CYAN,
                                        weight=ft.FontWeight.BOLD,
                                        size=13,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Text(
                                "🔔 VOCÊ SERÁ NOTIFICADO PELO WHATSAPP"
                                " ASSIM QUE SEU PEDIDO ESTIVER PRONTO!",
                                color="#FFFFFF",
                                weight=ft.FontWeight.BOLD,
                                size=12,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                texto_instrucao,
                                color=YELLOW,
                                size=11,
                                italic=True,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    padding=12,
                    bgcolor="#0B0C10",
                    border=ft.Border(
                        top=ft.BorderSide(2, CYAN),
                        bottom=ft.BorderSide(2, CYAN),
                        left=ft.BorderSide(2, CYAN),
                        right=ft.BorderSide(2, CYAN),
                    ),
                    border_radius=8,
                ),
            ],
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        ),
    )
    modal_final.actions = [
        ft.Button(
            content=ft.Text(
                "JÁ ENVIEI ✅",
                color="#0B0C10",
                weight=ft.FontWeight.BOLD,
            ),
            bgcolor=YELLOW,
            elevation=2,
            on_click=pedido_enviado,
        ),
        ft.TextButton("VOLTAR", on_click=lambda e: page.pop_dialog()),
    ]

    page.pop_dialog()  # fecha o resumo do pedido ou a tela do PIX
    page.show_dialog(modal_final)

  def btn_pix_click(e):
    finalizar_pedido("PIX")

  def voltar_do_pix(e):
    page.pop_dialog()
    page.show_dialog(modal_checkout)

  modal_pix = ft.AlertDialog(
      modal=True,
      bgcolor="#1F2833",
      title=ft.Text(
          "📱 PAGAMENTO VIA PIX", color=CYAN, weight=ft.FontWeight.BOLD
      ),
      content=ft.Container(
          width=400,
          content=ft.Column(
              [
                  ft.Text(
                      "1) Toque em COPIAR CÓDIGO PIX\n"
                      "2) No app do seu banco, escolha Pix > Copia e Cola\n"
                      "3) Pague e volte aqui para enviar o pedido",
                      color="#FFFFFF",
                      size=12,
                  ),
                  valor_pix_text,
                  ft.Container(
                      content=codigo_pix_ui,
                      padding=8,
                      bgcolor="#0B0C10",
                      border_radius=5,
                  ),
                  ft.Button(
                      content=ft.Text(
                          "📋 COPIAR CÓDIGO PIX",
                          color="#FFFFFF",
                          weight=ft.FontWeight.BOLD,
                      ),
                      style=ft.ButtonStyle(bgcolor={"": PURPLE}),
                      elevation=2,
                      on_click=copiar_codigo_pix,
                  ),
                  aviso_copia_ui,
                  ft.Text(
                      "Se o botão não copiar, segure o código acima com o"
                      " dedo e escolha Copiar.",
                      color="#A9A9A9",
                      size=11,
                  ),
                  ft.Text(
                      f"Chave PIX: {CHAVE_PIX_SALVADOR}",
                      color=YELLOW,
                      size=11,
                      selectable=True,
                  ),
              ],
              tight=True,
              horizontal_alignment=ft.CrossAxisAlignment.CENTER,
              spacing=10,
              scroll=ft.ScrollMode.AUTO,
          ),
      ),
      actions=[
          ft.Button(
              content=ft.Text(
                  "PAGUEI! ENVIAR PEDIDO 🚀",
                  color="#0B0C10",
                  weight=ft.FontWeight.BOLD,
              ),
              bgcolor=GREEN,
              elevation=2,
              on_click=btn_pix_click,
          ),
          ft.TextButton("VOLTAR", on_click=voltar_do_pix),
      ],
  )

  def selecionar_pagamento(forma):
    nonlocal forma_pagamento_selecionada
    forma_pagamento_selecionada = forma
    if forma == "PIX":
      btn_pix.style = ft.ButtonStyle(bgcolor={"": PURPLE})
      btn_retirada.style = ft.ButtonStyle(bgcolor={"": "#111"})
    else:
      btn_pix.style = ft.ButtonStyle(bgcolor={"": "#111"})
      btn_retirada.style = ft.ButtonStyle(bgcolor={"": PURPLE})
    page.update()

  btn_pix = ft.Button(
      content=ft.Text("📱 PIX", color="#FFFFFF", weight=ft.FontWeight.BOLD),
      style=ft.ButtonStyle(bgcolor={"": PURPLE}),
      expand=True,
      elevation=2,
      on_click=lambda e: selecionar_pagamento("PIX"),
  )

  btn_retirada = ft.Button(
      content=ft.Text(
          "🏪 PAGAR NA RETIRADA", color="#FFFFFF", weight=ft.FontWeight.BOLD
      ),
      style=ft.ButtonStyle(bgcolor={"": "#111"}),
      expand=True,
      elevation=2,
      on_click=lambda e: selecionar_pagamento("PAGAR NA RETIRADA"),
  )

  def abrir_revisao(e):
    lista_revisao_ui.controls.clear()
    total_geral = 0.0

    for item in carrinho:
      total_geral += item["preco_total"]
      detalhes_texto = ""
      if item["sem"]:
        detalhes_texto += f"❌ Sem: {', '.join(item['sem'])}\n"
      if item["com"]:
        detalhes_texto += f"🟢 Adicionais: {', '.join(item['com'])}"

      lista_revisao_ui.controls.append(
          ft.Container(
              content=ft.Column([
                  ft.Row(
                      [
                          ft.Text(
                              f"{item['quantidade']}x {item['nome']}",
                              weight=ft.FontWeight.BOLD,
                              color="#FFFFFF",
                          ),
                          ft.Text(f"R$ {item['preco_total']:.2f}", color=CYAN),
                      ],
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                  ),
                  (
                      ft.Text(detalhes_texto, color=YELLOW, size=12)
                      if detalhes_texto
                      else ft.Container()
                  ),
              ]),
              padding=5,
          )
      )

    total_revisao_ui.value = f"TOTAL A PAGAR: R$ {total_geral:.2f}"
    page.show_dialog(modal_checkout)

  def processar_pagamento(e):
    nonlocal codigo_pix_atual
    if not txt_nome_player.value.strip():
      txt_nome_player.error_text = "Informe seu nome para identificar o pedido"
      page.update()
      return
    txt_nome_player.error_text = None

    if forma_pagamento_selecionada == "PIX":
      total_geral = sum(item["preco_total"] for item in carrinho)
      codigo_pix_atual = gerar_pix_copia_e_cola(
          CHAVE_PIX_SALVADOR, total_geral, NOME_PIX, CIDADE_PIX
      )
      codigo_pix_ui.value = codigo_pix_atual
      valor_pix_text.value = f"R$ {total_geral:.2f}"
      aviso_copia_ui.value = ""
      page.pop_dialog()  # fecha o resumo do pedido
      page.show_dialog(modal_pix)
    else:
      finalizar_pedido("PAGAR NA RETIRADA")

  modal_checkout = ft.AlertDialog(
      modal=True,
      bgcolor="#1F2833",
      title=ft.Text(
          "⚔️ REVISAR SEU COMBO", color=CYAN, weight=ft.FontWeight.BOLD
      ),
      content=ft.Container(
          width=400,
          content=ft.Column(
              [
                  ft.Divider(color=PURPLE),
                  lista_revisao_ui,
                  ft.Divider(color=PURPLE),
                  total_revisao_ui,
                  txt_nome_player,
                  ft.Text(
                      "FORMA DE PAGAMENTO:",
                      color=YELLOW,
                      size=12,
                      weight=ft.FontWeight.BOLD,
                  ),
                  ft.Row([btn_pix, btn_retirada], spacing=10),
              ],
              tight=True,
              spacing=12,
              scroll=ft.ScrollMode.AUTO,
          ),
      ),
      actions=[
          ft.Button(
              content=ft.Text(
                  "ENVIAR PEDIDO 🚀",
                  color="#0B0C10",
                  weight=ft.FontWeight.BOLD,
              ),
              bgcolor=GREEN,
              elevation=2,
              on_click=processar_pagamento,
          ),
          ft.TextButton("VOLTAR", on_click=lambda e: page.pop_dialog()),
      ],
  )

  lista_lanches_ui = ft.Column(spacing=10)
  for lanche in cardapio:
    texto_ingredientes = ", ".join(lanche["ingredientes"])
    lista_lanches_ui.controls.append(
        ft.Container(
            content=ft.Row(
                [
                    ft.Image(
                        src=lanche["imagem"],
                        width=65,
                        height=65,
                        border_radius=8,
                        fit="cover",
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                f"{lanche['id']}. {lanche['nome']}",
                                weight=ft.FontWeight.BOLD,
                                size=15,
                                color="#FFFFFF",
                            ),
                            ft.Text(
                                texto_ingredientes,
                                size=11,
                                color="#A9A9A9",
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        expand=True,
                    ),
                    ft.Button(
                        content=ft.Text(
                            f"R$ {lanche['preco']:.2f}",
                            color="#FFFFFF",
                            weight=ft.FontWeight.BOLD,
                            size=12,
                        ),
                        style=ft.ButtonStyle(bgcolor={"": PURPLE}),
                        elevation=2,
                        on_click=lambda e, l=lanche: abrir_customizacao(l),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=10,
            ),
            padding=10,
            bgcolor="#1F2833",
            border_radius=8,
            border=ft.Border(
                top=ft.BorderSide(1, "#333333"),
                bottom=ft.BorderSide(1, "#333333"),
                left=ft.BorderSide(1, "#333333"),
                right=ft.BorderSide(1, "#333333"),
            ),
        )
    )

  btn_ver_pedido = ft.Button(
      content=ft.Text(
          "🛒 VER MEU PEDIDO", color="#0B0C10", weight=ft.FontWeight.BOLD
      ),
      bgcolor=YELLOW,
      elevation=2,
      visible=False,
      on_click=abrir_revisao,
  )

  # Cabeçalho
  cabecalho_perfil = ft.Row(
      [
          ft.Container(
              content=ft.Image(
                  src=FOTO_SALVADOR,
                  width=80,
                  height=80,
                  border_radius=40,
                  fit="cover",
                  error_content=ft.Icon(
                      ft.Icons.ACCOUNT_CIRCLE, color=CYAN, size=80
                  ),
              ),
              border=ft.Border(
                  top=ft.BorderSide(2, CYAN),
                  bottom=ft.BorderSide(2, CYAN),
                  left=ft.BorderSide(2, CYAN),
                  right=ft.BorderSide(2, CYAN),
              ),
              border_radius=40,
          ),
          ft.Column(
              [
                  ft.Text(
                      "SALVADOR LANCHES 🍔",
                      size=18,
                      weight=ft.FontWeight.BOLD,
                      color=CYAN,
                  ),
                  ft.Text(
                      "MONTE SEU PEDIDO ONLINE",
                      size=11,
                      color=PURPLE,
                      weight=ft.FontWeight.BOLD,
                  ),
              ],
              spacing=2,
          ),
      ],
      alignment=ft.MainAxisAlignment.CENTER,
      spacing=15,
  )

  page.add(
      ft.Container(
          content=ft.Column([
              cabecalho_perfil,
              ft.Divider(color=PURPLE),
              ft.Row(
                  [
                      ft.Text(
                          "🍔 CARDÁPIO:",
                          size=14,
                          color=GREEN,
                          weight=ft.FontWeight.BOLD,
                      ),
                      btn_ver_pedido,
                  ],
                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
              ),
              lista_lanches_ui,
          ]),
          padding=15,
      )
  )


ft.run(main)
