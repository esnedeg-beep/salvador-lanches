import threading
import urllib.parse
import webbrowser
import flet as ft
from config import (
    FOTO_SALVADOR,
    CHAVE_PIX_SALVADOR,
    NUMERO_WHATSAPP_SALVADOR,
    CARDAPIO,
    BEBIDAS,
    TABELA_ADICIONAIS,
)


def main(page: ft.Page):
  page.title = "SALVADOR LANCHES - CLIENTE"
  page.theme_mode = ft.ThemeMode.DARK
  page.bgcolor = "#0B0C10"
  page.scroll = ft.ScrollMode.AUTO
  page.window_width = 450
  page.window_height = 800

  # Cores Neon
  CYAN = "#00FFFF"
  PURPLE = "#9D00FF"
  GREEN = "#39FF14"
  YELLOW = "#FFD700"
  
  
  # Carrinho de compras do cliente
  carrinho = []

  # Variáveis temporárias de estado
  item_atual = None
  tipo_item_atual = None  # "lanche" ou "bebida"
  quantidade_atual = 1
  ingredientes_removidos = []
  adicionais_escolhidos = []
  forma_pagamento_selecionada = "PIX"

  # Componentes de UI
  lista_revisao_ui = ft.Column(spacing=5)
  total_revisao_ui = ft.Text(
      "", size=18, color=YELLOW, weight=ft.FontWeight.BOLD
  )
  status_missao_ui = ft.Column(
      spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER
  )

  txt_nome_player = ft.TextField(
      label="SEU NOME (CLIENTE)",
      border_color=CYAN,
      focused_border_color=GREEN,
      text_style=ft.TextStyle(color="#FFFFFF"),
  )

  

  # --- CUSTOMIZAÇÃO / QUANTIDADE ---
  img_modal_item = ft.Image(
      src="", width=60, height=60, border_radius=8, fit="cover"
  )
  container_ingredientes_ui = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)
  container_adicionais_ui = ft.Column(spacing=2, scroll=ft.ScrollMode.AUTO)
  div_ingredientes_ui = ft.Divider(color=PURPLE)
  div_adicionais_ui = ft.Divider(color=PURPLE)
  txt_titulo_ingredientes = ft.Text(
      "❌ RETIRAR INGREDIENTES (Desmarque para remover):",
      color=YELLOW,
      size=12,
      weight=ft.FontWeight.BOLD,
  )
  txt_titulo_adicionais = ft.Text(
      "⚡ TURBINAR LANCHE (Adicionais):",
      color=GREEN,
      size=12,
      weight=ft.FontWeight.BOLD,
  )

  def abrir_customizacao(item_selecionado, tipo):
    nonlocal item_atual, tipo_item_atual, quantidade_atual, ingredientes_removidos, adicionais_escolhidos
    item_atual = item_selecionado
    tipo_item_atual = tipo
    quantidade_atual = 1
    ingredientes_removidos = []
    adicionais_escolhidos = []

    txt_quantidade.value = str(quantidade_atual)
    img_modal_item.src = item_atual["imagem"]

    if tipo == "lanche":
      div_ingredientes_ui.visible = True
      div_adicionais_ui.visible = True
      txt_titulo_ingredientes.visible = True
      txt_titulo_adicionais.visible = True
      container_ingredientes_ui.visible = True
      container_adicionais_ui.visible = True

      container_ingredientes_ui.controls.clear()
      for ing in item_atual["ingredientes"]:
        container_ingredientes_ui.controls.append(
            ft.Checkbox(
                label=ing.capitalize(),
                value=True,
                label_style=ft.TextStyle(color="#FFFFFF"),
                active_color=PURPLE,
                on_change=lambda e, i=ing: gerenciar_ingredientes(e, i),
            )
        )

      
  # --- ENVIO DO WHATSAPP + TELA DE STATUS ---
  def executar_envio_whatsapp(tipo_pagamento):
    nome_cliente = txt_nome_player.value.strip().upper()
    total_geral = sum(item["preco_total"] for item in carrinho)

    msg = f"🍔 *NOVO PEDIDO - SALVADOR LANCHES*\n"
    msg += f"👤 *Cliente:* {nome_cliente}\n"
    msg += f"-----------------------------------\n"

    for item in carrinho:
      msg += f"• *{item['quantidade']}x {item['nome']}* - R$ {item['preco_total']:.2f}\n"
      if item.get("sem"):
        msg += f"   ❌ Sem: {', '.join(item['sem'])}\n"
      if item.get("com"):
        msg += f"   🟢 Com: {', '.join(item['com'])}\n"

    msg += f"-----------------------------------\n"
    msg += f"💰 *TOTAL:* R$ {total_geral:.2f}\n"
    msg += f"📱 *Forma de Pagamento:* {tipo_pagamento}\n\n"

    if tipo_pagamento == "PIX":
      msg += (
          "📌 *Anexando o comprovante do PIX abaixo para confirmar o"
          " preparo!*"
      )
    else:
      msg += "📌 *Pagamento será realizado no momento da retirada!*"

    msg_url = urllib.parse.quote(msg)
    link_whatsapp = (
        f"https://wa.me/{NUMERO_WHATSAPP_SALVADOR}?text={msg_url}"
    )

    threading.Thread(
        target=lambda: webbrowser.open(link_whatsapp), daemon=True
    ).start()

    modal_pix.open = False
    modal_checkout.open = False
    btn_ver_pedido.visible = False
    carrinho.clear()

    texto_instrucao = (
        "Envie o comprovante na conversa para iniciar o preparo!"
        if tipo_pagamento == "PIX"
        else "Aguarde a confirmação da recepção pelo WhatsApp!"
    )

    status_missao_ui.controls.clear()
    status_missao_ui.controls.extend([
        ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.TIMER, color=YELLOW, size=50),
                    ft.Text(
                        "⚡ PEDIDO ENVIADO! ⚡",
                        color=YELLOW,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        f"Cliente: {nome_cliente}",
                        color=CYAN,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Tempo estimado de preparo:", color="#FFFFFF", size=13
                    ),
                    ft.Container(
                        content=ft.Text(
                            "⏱️ 15 A 25 MINUTOS",
                            color="#0B0C10",
                            weight=ft.FontWeight.BOLD,
                            size=18,
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
                        margin=ft.Margin(0, 10, 0, 0),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=15,
            bgcolor="#1F2833",
            border_radius=10,
            border=ft.Border(
                top=ft.BorderSide(1, PURPLE),
                bottom=ft.BorderSide(1, PURPLE),
                left=ft.BorderSide(1, PURPLE),
                right=ft.BorderSide(1, PURPLE),
            ),
        )
    ])
    page.update()
    valor_pix_text = ft.Text(
    "",
    size=20,
    color=GREEN,
    weight=ft.FontWeight.BOLD,
)
      
  def btn_pix_click(e):
    executar_envio_whatsapp("PIX")

  def btn_retirada_click(e):
    executar_envio_whatsapp("PAGAR NA RETIRADA")

  modal_pix = ft.AlertDialog(
      bgcolor="#1F2833",
      title=ft.Text(
          "📱 PAGAMENTO VIA PIX", color=CYAN, weight=ft.FontWeight.BOLD
      ),
valor_pix_text = ft.Text("")
     
      content=ft.Container(
          width=400,
          content=ft.Column(
              [
                  ft.Text(
                      "Escaneie o QR Code ou copie a chave para realizar o"
                      " pagamento:",
                      color="#FFFFFF",
                      size=12,
                  ),
                  
                  
                  ft.Container(
                      content=ft.Column(
                          [
                          
                             ft.Icon(ft.Icons.QR_CODE_2, size=140, color=CYAN),
                              valor_pix_text,
                          ],
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                      ),
                      alignment=ft.Alignment(0, 0),
                      padding=10,
                  ),
                  ft.Text(
                      f"Chave PIX: {CHAVE_PIX_SALVADOR}",
                      color=YELLOW,
                      size=12,
                      weight=ft.FontWeight.BOLD,
                  ),
                  ft.Button(
                      content=ft.Text(
                          "📋 COPIAR CHAVE PIX",
                          color="#FFFFFF",
                          weight=ft.FontWeight.BOLD,
                      ),
                      style=ft.ButtonStyle(bgcolor={"": PURPLE}),
                      elevation=2,
                      on_click=copiar_chave_pix,
                  ),
              ],
              tight=True,
              horizontal_alignment=ft.CrossAxisAlignment.CENTER,
              spacing=10,
          ),
      ),
      actions=[
          ft.Button(
              content=ft.Text(
                  "PAGUEI! ENVIAR COMPROVANTE 🚀",
                  color="#0B0C10",
                  weight=ft.FontWeight.BOLD,
              ),
              bgcolor=GREEN,
              elevation=2,
              on_click=btn_pix_click,
          ),
          ft.TextButton(
              "VOLTAR",
              on_click=lambda e: setattr(modal_pix, "open", False)
              or page.update(),
          ),
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

  # Função para remover itens do carrinho
  def remover_do_carrinho(idx):
    item_removido = carrinho.pop(idx)
    page.snack_bar = ft.SnackBar(
        content=ft.Text(f"🗑️ {item_removido['nome']} removido do carrinho!"),
        bgcolor="red",
    )
    page.snack_bar.open = True
    
    if len(carrinho) == 0:
      modal_checkout.open = False
      btn_ver_pedido.visible = False
      page.update()
    else:
      btn_ver_pedido.content = ft.Text(
          f"🛒 VER MEU PEDIDO ({len(carrinho)} ITEM/NS)",
          color="#0B0C10",
          weight=ft.FontWeight.BOLD,
      )
      page.update()
      abrir_revisao(None) # Recarrega a tela de revisão

  def abrir_revisao(e):
    lista_revisao_ui.controls.clear()
    total_geral = 0.0

    for i, item in enumerate(carrinho):
      total_geral += item["preco_total"]
      detalhes_texto = ""
      if item.get("sem"):
        detalhes_texto += f"❌ Sem: {', '.join(item['sem'])}\n"
      if item.get("com"):
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
                              expand=True,
                          ),
                          ft.Text(f"R$ {item['preco_total']:.2f}", color=CYAN),
                          # Linha vertical separando o ícone de lixeira
                          ft.Container(width=1, height=20, bgcolor=PURPLE),
                          ft.IconButton(
                              icon=ft.Icons.DELETE_OUTLINE,
                              icon_color="red", # <--- CORRIGIDO AQUI
                              icon_size=20,
                              tooltip="Remover item",
                              on_click=lambda e, idx=i: remover_do_carrinho(idx),
                          ),
                      ],
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                      vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
    modal_checkout.open = True
    page.update()

  def processar_pagamento(e):
    if not txt_nome_player.value.strip():
      page.snack_bar = ft.SnackBar(
          content=ft.Text(
              "⚠️ Por favor, informe seu nome para identificar o pedido!",
              color="#FFFFFF",
          ),
          bgcolor="red",
      )
      page.snack_bar.open = True
      page.update()
      return

    if forma_pagamento_selecionada == "PIX":
      modal_checkout.open = False
      total_geral = sum(item["preco_total"] for item in carrinho)
      valor_pix_text.value = f"R$ {total_geral:.2f}"
      modal_pix.open = True
      page.update()
    else:
      executar_envio_whatsapp("PAGAR NA RETIRADA")

  modal_checkout = ft.AlertDialog(
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
          ft.TextButton(
              "VOLTAR",
              on_click=lambda e: setattr(modal_checkout, "open", False)
              or page.update(),
          ),
      ],
  )

  # Adiciona os modais ao overlay
  page.overlay.extend([
      modal_customizar,
      modal_checkout,
      modal_pix,
  ])

  # Lista de Lanches UI
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
                        on_click=lambda e, l=lanche: abrir_customizacao(
                            l, "lanche"
                        ),
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

  


ft.run(main)
