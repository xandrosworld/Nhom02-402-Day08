from textwrap import fill
import gradio as gr
from rag_answer import rag_answer

def chat_logic(message, history):
    """
    Hàm xử lý logic chat: Gọi RAG pipeline và định dạng lại Output để hiển thị
    citation (nguồn trích dẫn) một cách chuyên nghiệp.
    """
    # Gọi RAG pipeline với cấu hình chuẩn nhất hiện tại
    try:
        result = rag_answer(
            query=message,
            retrieval_mode="hybrid",
            use_rerank=True,
            use_transform=True,
            top_k_search=15,
            top_k_select=3,
            verbose=False
        )
        
        answer = result["answer"]
        sources = result["sources"]
        
        # Định dạng thêm phần hiển thị Nguồn trích dẫn (Citations)
        if sources:
            formatted_sources = "\n\n---\n**📚 Nguồn tham khảo (Citations):**\n"
            for s in sources:
                formatted_sources += f"- `{s}`\n"
            final_answer = answer + formatted_sources
        else:
            final_answer = answer + "\n\n---\n*Không tìm thấy thông tin trong hệ thống tài liệu.*"
            
        return final_answer

    except Exception as e:
        return f"❌ **Lỗi Hệ thống:** {str(e)}"

# Khởi tạo giao diện Chat có sẵn của Gradio
with gr.Blocks(fill_height=True) as demo:
    gr.ChatInterface(
        fn=chat_logic,
        title="CS/IT Helpdesk Assistant 🤖",
        description="Hệ thống hỏi đáp dựa trên tài liệu nội bộ công ty (RAG Pipeline: Hybrid Search + Voyage Reranker + Claude).",
        examples=[
            "SLA xử lý ticket P1 là bao lâu?",
            "Xin cấp quyền Admin Level 4 cho Contractor có được không?",
            "Sản phẩm Flash Sale đã kích hoạt sử dụng có được hoàn tiền không?",
            "Xảy ra sự cố ticket P1 lúc 2 giờ sáng thì quy trình cấp quyền truy cập diễn ra thế nào?"
        ],
        fill_height=True,
        submit_btn="Gửi yêu cầu"
    )

if __name__ == "__main__":
    print("🚀 Đang khởi động giao diện Chat UI...")
    # Bật share=True nếu bạn muốn chia sẻ public link cho Giảng viên xem
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, theme=gr.themes.Soft())
