"""
PDF生成（配布用ビュー）

Zone: Logic（Plan必須）
責務: セッションデータのPDF化

設計思想:
- JSON（正本）から生成可能
- ユーザー体験用の成果物
- 日本語対応（reportlab使用）
"""
from pathlib import Path
from datetime import datetime
import tempfile

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.koyomi.chat.session import ConsultationSession


def _setup_japanese_font():
    """日本語フォント設定
    
    Note:
        MVPでは標準フォント使用
        将来的にNotoSans JPなど追加
    """
    # TODO: 日本語フォント追加
    # pdfmetrics.registerFont(TTFont('NotoSansJP', 'NotoSansJP-Regular.ttf'))
    pass


def export_pdf(session: ConsultationSession, output_path: str = None) -> str:
    """セッションをPDF出力
    
    Args:
        session: 出力するセッション
        output_path: 出力先パス（Noneの場合は一時ファイル）
    
    Returns:
        生成したPDFのパス
    """
    # 出力先決定
    if output_path is None:
        # 一時ファイル（単発利用）
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix='.pdf',
            prefix=f'koyomi_{session.session_id}_'
        )
        output_path = temp_file.name
        temp_file.close()
    
    # PDF生成
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # ストーリー（コンテンツ）
    story = []
    
    # スタイル設定
    styles = getSampleStyleSheet()
    
    # タイトルスタイル
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # セクションスタイル
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # 本文スタイル
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=18
    )
    
    # タイトル
    story.append(Paragraph("暦 KOYOMI 鑑定結果", title_style))
    story.append(Spacer(1, 10*mm))
    
    # 基本情報
    story.append(Paragraph("基本情報", section_style))
    
    birth_date_str = session.birth_data.get('datetime', '不明')
    has_time = session.birth_data.get('has_time', False)
    
    basic_info = [
        ['生年月日', birth_date_str],
        ['時刻', '有り' if has_time else '不明（三柱推命）'],
        ['鑑定日時', datetime.fromisoformat(session.created_at).strftime('%Y年%m月%d日 %H:%M')]
    ]
    
    basic_table = Table(basic_info, colWidths=[40*mm, 120*mm])
    basic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    story.append(basic_table)
    story.append(Spacer(1, 10*mm))
    
    # 命式
    story.append(Paragraph("命式（四柱）", section_style))
    
    pillars = session.pillars
    pillars_data = [
        ['', '年柱', '月柱', '日柱', '時柱' if has_time else '時柱（不明）'],
        ['天干', 
         pillars.get('year', {}).get('kan', '-'),
         pillars.get('month', {}).get('kan', '-'),
         pillars.get('day', {}).get('kan', '-'),
         pillars.get('hour', {}).get('kan', '-') if has_time else '-'
        ],
        ['地支',
         pillars.get('year', {}).get('shi', '-'),
         pillars.get('month', {}).get('shi', '-'),
         pillars.get('day', {}).get('shi', '-'),
         pillars.get('hour', {}).get('shi', '-') if has_time else '-'
        ]
    ]
    
    pillars_table = Table(pillars_data, colWidths=[30*mm, 32.5*mm, 32.5*mm, 32.5*mm, 32.5*mm])
    pillars_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    
    story.append(pillars_table)
    story.append(Spacer(1, 10*mm))
    
    # 用神
    story.append(Paragraph("用神（活かすべきエネルギー）", section_style))
    yojin_text = ' → '.join(session.yojin)
    story.append(Paragraph(yojin_text, body_style))
    story.append(Spacer(1, 10*mm))
    
    # メタファー
    metaphor = session.metaphor
    
    story.append(Paragraph("あなたの本質", section_style))
    story.append(Paragraph(metaphor.get('本質', ''), body_style))
    story.append(Spacer(1, 5*mm))
    
    story.append(Paragraph("強み", section_style))
    story.append(Paragraph(metaphor.get('強み', ''), body_style))
    story.append(Spacer(1, 5*mm))
    
    story.append(Paragraph("課題", section_style))
    story.append(Paragraph(metaphor.get('課題', ''), body_style))
    story.append(Spacer(1, 5*mm))
    
    story.append(Paragraph("アドバイス", section_style))
    story.append(Paragraph(metaphor.get('アドバイス', ''), body_style))
    story.append(Spacer(1, 10*mm))
    
    # 相談内容（ある場合）
    if session.query:
        story.append(Paragraph("ご相談内容", section_style))
        story.append(Paragraph(session.query, body_style))
        story.append(Spacer(1, 10*mm))
    
    # まとめ（ある場合）
    if session.summary:
        story.append(Paragraph("鑑定まとめ", section_style))
        story.append(Paragraph(session.summary, body_style))
        story.append(Spacer(1, 10*mm))
    
    # フッター
    story.append(Spacer(1, 20*mm))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    # データ保存ポリシー明記（重要）
    if session.is_subscription():
        policy_style = ParagraphStyle(
            'Policy',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#e74c3c'),
            alignment=TA_CENTER,
            leading=12
        )
        story.append(Paragraph(
            "【重要】本データはサブスクリプション契約期間中のみ保存されます。",
            policy_style
        ))
        story.append(Paragraph(
            "契約終了後、自動的に削除され、復元はできません。",
            policy_style
        ))
        story.append(Spacer(1, 5*mm))
    
    story.append(Paragraph("暦 KOYOMI - 運命とは命の運び", footer_style))
    story.append(Paragraph("依存ではなく、自立のお手伝い", footer_style))
    
    # PDF生成
    doc.build(story)
    
    return output_path


def export_pdf_from_json(json_path: str, output_path: str = None) -> str:
    """JSONファイルからPDF生成
    
    Args:
        json_path: JSONファイルパス
        output_path: 出力先パス（Noneの場合は一時ファイル）
    
    Returns:
        生成したPDFのパス
    
    Note:
        将来的な再生成用
        JSONが正本であることの証明
    """
    import json
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    session = ConsultationSession(**data)
    return export_pdf(session, output_path)
