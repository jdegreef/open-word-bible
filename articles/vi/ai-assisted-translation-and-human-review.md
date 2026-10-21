---
title: "Dịch với sự hỗ trợ của AI và việc duyệt của con người: một câu văn trở thành \"đã duyệt\" như thế nào"
summary: Mọi thứ trên trang này hiện nay đều được dịch với sự hỗ trợ của AI. Đây là cách một câu văn được soạn nháp, bản ghi của nó chứa những gì, điều mà việc soạn nháp bằng AI không làm được, và một câu văn chuyển sang trạng thái đã duyệt như thế nào.
date: 2026-10-10
order: 10
section: method
source: c1cfadc5bb1a
---
Open Word Bible được dịch với sự trợ giúp của AI. Chúng tôi nói rõ điều đó, vì một dự án hứa sẽ trình bày công việc của mình thì không thể mập mờ về chuyện ai đã làm công việc ấy. Bài này giải thích một câu văn được soạn nháp như thế nào, bạn có thể thấy được gì về nó, việc soạn nháp bằng AI còn thiếu sót ở đâu, và điều gì phải xảy ra trước khi bất kỳ câu văn nào được gọi là đã duyệt.

## Một câu văn được soạn nháp như thế nào

Hãy lấy Phi-líp 4:6–7, một câu văn tiếng Hy Lạp dài nói về sự lo lắng và sự cầu nguyện. Câu ấy đi qua bốn bước.

**1. Bản văn nguồn được nạp vào, không phải gõ tay.** Một chương trình đọc dữ liệu nguồn đã được cố định phiên bản: bản Tân Ước Hy Lạp SBL cùng dữ liệu từ ngữ MACULA cho Tân Ước, và Codex Leningrad bản Westminster cho Cựu Ước. Nó tách bản văn ở chỗ ấn bản kết thúc một câu văn và viết một bản ghi trống cho mỗi câu, kèm mã định danh của từng chữ Hy Lạp và chính bản văn Hy Lạp. Không ai, dù là người hay AI, gõ nguyên văn. Xin xem [Vì sao chúng tôi không bao giờ gõ tay tiếng Hy Lạp hay tiếng Hê-bơ-rơ](/articles/never-typed-by-hand/).

**2. AI viết bản nháp.** Làm việc từ tiếng Hy Lạp, dữ liệu từ ngữ và một bản hướng dẫn văn phong viết sẵn, một mô hình AI điền vào bản ghi: một bản dịch sát từng chữ theo trật tự từ của tiếng Hy Lạp, bản dịch ở ba cấp độ trong mỗi ngôn ngữ, và những quyết định đằng sau chúng. Bản hướng dẫn văn phong đặt ra các quy tắc: những chữ tiếng Anh nào là thuật ngữ chính đã được định sẵn, mỗi cấp độ khác nhau ra sao, điều gì được đặt trong ngoặc vuông, cài đặt đọc nào áp dụng ở đâu. Với một số sách, có thêm một danh sách riêng các thuật ngữ đã định, để cùng một chữ Hê-bơ-rơ không bị dịch ra ba cách khác nhau qua sáu mươi sáu chương của sách Ê-sai.

**3. Phần mềm kiểm tra các quy tắc.** Một chương trình kiểm định chạy trên mọi bản ghi. Nó loại bỏ bất kỳ chữ Hy Lạp hay Hê-bơ-rơ nào không trùng khớp từng chữ cái với một dạng chữ hay một mục từ điển trong dữ liệu nguồn. Nó kiểm tra rằng mỗi thuật ngữ chính dùng đúng chữ tiếng Anh đã định ở mọi cấp độ, trừ khi có một quyết định giải thích vì sao không. Nó kiểm tra rằng mọi bản ghi đều có đủ ba cấp độ, rằng một bản ghi kết thúc ở chỗ một câu văn kết thúc, và rằng các quyết định về nghĩa không chứa cách diễn đạt riêng của bất kỳ ngôn ngữ nào. Một bản ghi vi phạm quy tắc sẽ không được đưa vào.

**4. Thay đổi được thực hiện công khai.** Mỗi đoạn mới được gửi đến dưới dạng một đề xuất thay đổi trên GitHub, nơi các bài kiểm tra và việc dựng trang web chạy trước khi đề xuất được hợp nhất. Toàn bộ lịch sử của nó vẫn còn đó cho ai muốn đọc.

## Bản ghi chứa những gì

Đây là cấp độ Cân bằng của câu văn được tạo ra qua các bước ấy:

> {{OWB:PHP.4.6.s1:B}}

Bản ghi của câu này chứa tiếng Hy Lạp, mở đầu bằng {{GREEK:PHP.4.6:1-2}}, "chẳng điều gì hãy lo lắng"; một bản dịch sát từng chữ; các cấp độ Sát nghĩa, Cân bằng và Dễ đọc bằng tiếng Anh; và cũng ba cấp độ ấy trong các ngôn ngữ khác khi chúng được soạn nháp. Nó cũng chứa mười hai quyết định. Bảy quyết định là về nghĩa, chung cho mọi ngôn ngữ. Một quyết định nói rằng {{LEMMA:PHP.4.6:2}} ở đây có nghĩa là sự lo âu phiền muộn, chữ Đức Giê-xu dùng trong Ma-thi-ơ 6, chứ không phải sự quan tâm tốt lành mà Phao-lô dùng chữ ấy để nói đến trong 2:20. Một quyết định khác nói rằng động từ "canh giữ" là việc mà một đội quân đồn trú làm, một hình ảnh mà người thành Phi-líp, một thuộc địa La Mã có những người lính giải ngũ trong số công dân, hẳn đã cảm nhận được. Năm quyết định còn lại là quyết định về cách diễn đạt, mỗi quyết định cho một ngôn ngữ. Chẳng hạn, một quyết định cho tiếng Anh giải thích vì sao bản Cân bằng nói sự bình an sẽ "stand guard over" (đứng canh giữ) lòng anh em: nó giữ hình ảnh người lính mà không dùng chữ cổ "keep" (gìn giữ).

Hai quyết định trong bản ghi này được đánh dấu là chưa chắc chắn. Một quyết định là về nghĩa: sự bình an "vượt quá mọi sự hiểu biết" có thể là sự bình an vượt ngoài điều trí óc có thể nắm bắt, hoặc sự bình an đạt được nhiều hơn mọi kế hoạch của con người. Bản ghi theo cách hiểu phổ biến hơn và đưa cách kia vào chú thích. Quyết định thứ hai là về tiếng Anh. Cấp độ Dễ đọc nói sự bình an canh giữ anh em "because you are joined to Christ Jesus" (vì anh em được kết hợp với Đấng Christ Giê-xu), trong khi tiếng Hy Lạp chỉ nói "trong". Quyết định về cách diễn đạt nói thẳng rằng cách này thêm vào một lý do mà tiếng Hy Lạp không nói ra, và rằng những người duyệt nên kiểm tra lại:

> {{OWB:PHP.4.6.s1:R}}

Ở đâu cũng theo khuôn mẫu ấy. Trong các bản nháp cho đến nay, trung bình mỗi câu văn mang khoảng bốn quyết định, và cứ khoảng mười hai quyết định thì có một được đánh dấu là chưa chắc chắn. AI được dặn phải đánh dấu một lựa chọn sít sao là chưa chắc chắn thay vì trình bày nó như đã ngã ngũ, và trang đọc hiển thị nhãn ấy.

## Điều AI không làm

AI không tự quyết định rằng công việc của mình là đúng. **Không có gì được đánh dấu là đã duyệt bởi AI.** Mọi câu văn bắt đầu với trạng thái *Bản nháp · chưa được duyệt*, và giữ nguyên như vậy cho đến khi một người duyệt có tên chấp thuận. Trong cơ sở dữ liệu của dự án, mỗi bước trong quá trình duyệt một câu văn đều thuộc về tài khoản của một người có tên; AI không có cách nào tự chấp thuận bản nháp của chính mình.

AI cũng không dùng các bản dịch khác làm cơ sở. Các bản Kinh Thánh tiếng Anh thuộc phạm vi công cộng có thể được tham khảo để kiểm tra một bản nháp, nhưng không bao giờ để cung cấp lời văn cho nó, và lời văn của các bản dịch có bản quyền không bao giờ được sao chép lại.

## Giới hạn của việc soạn nháp bằng AI

Người đọc có lý khi hỏi AI sai ở những chỗ nào. Chúng tôi đã thấy nhiều loại sai sót, và quy trình được xây dựng xoay quanh chúng.

**Lời văn quen thuộc có sức kéo rất mạnh.** Một mô hình AI đã đọc nhiều bản Kinh Thánh. Những bản nháp đầu tiên của Phi-líp 4:6–8 gần như giống từng chữ với các bản dịch hiện có, và phải được viết lại từ tiếng Hy Lạp. Bản hướng dẫn văn phong giờ đây dặn mọi bản nháp phải bắt đầu từ tiếng Hy Lạp và bản dịch sát từng chữ, so sánh sau, và viết lại bất kỳ câu nào trùng với một bản dịch nổi tiếng nhiều hơn một cụm từ ngắn thông thường.

**Dữ kiện có thể bị nhớ sai.** Khi một bản ghi mô tả bằng chứng từ các bản chép tay, cách đọc của một cuộn sách Hê-bơ-rơ hay một tác giả trong Hội Thánh đầu tiên, nó dựa vào điều mô hình đã học được, chứ không dựa vào một thư viện mở sẵn trước mặt. Các bản ghi được dặn phải nói rõ điều đó. Nhiều quyết định về các dị bản kết thúc bằng một ghi chú rằng người duyệt phải đối chiếu bằng chứng với bộ khảo dị, tức là danh sách học thuật các cách đọc trong các bản chép tay. Một số bản ghi của sách Ê-sai còn đi xa hơn và đánh dấu một cách đọc là "theo trí nhớ; cần kiểm tra". Xin xem [Khi các bản chép tay không thống nhất](/articles/when-manuscripts-disagree/).

**Trôi chảy không phải là phán đoán đúng.** Một bản nháp có thể đọc rất trơn tru mà vẫn sai, hoặc đúng vì những lý do không hẳn là những lý do đã nêu. Giọng văn tự tin của một câu không phải là bằng chứng cho nó.

**Lời văn tự nhiên cần đến người bản ngữ.** AI có thể viết tiếng Tây Ban Nha, tiếng Pháp, tiếng Swahili, tiếng Việt hay tiếng Hàn đúng ngữ pháp. Câu văn ấy nghe có tự nhiên với một người lớn lên cùng ngôn ngữ đó hay không lại là chuyện khác. Chẳng hạn, bản ghi tiếng Tây Ban Nha cho Giăng 1:1 chọn *el Verbo* thay vì *la Palabra* cho "Ngôi Lời", và đánh dấu lựa chọn ấy để một người bản ngữ duyệt lại.

**Giữ sự nhất quán giữa các sách là điều khó.** Hàng nghìn câu văn được soạn nháp vào những thời điểm khác nhau có thể dần lệch nhau. Các thuật ngữ chính được phần mềm kiểm tra, danh sách thuật ngữ cho các sách dài, và những quyết định dẫn lại các quyết định trước đều chống lại điều đó, nhưng vẫn sẽ còn một số chỗ lệch để người duyệt tìm ra.

## Vậy sao lại dùng AI?

Một người hoài nghi chín chắn có thể nói rằng Kinh Thánh quá quan trọng để soạn nháp bằng máy. Chúng tôi xem điều đó là nghiêm túc. Câu trả lời của chúng tôi là AI không thay thế các học giả; nó thay đổi điều mà họ được yêu cầu làm.

Viết ra lý do cho từng câu văn của Kinh Thánh, bằng ngôn ngữ dễ hiểu, kèm những phương án đã được cân nhắc, là khối lượng công việc lớn hơn mức mà hầu hết các nhóm dịch từng có thời gian để làm. Một bản nháp trình bày rõ lập luận của mình cho người duyệt một điều cụ thể để kiểm tra: một lựa chọn được nêu ra, những phương án bị gạt sang bên, và một lý do hoặc đứng vững hoặc không. Nó cũng cho mọi người đọc cùng một cái nhìn mà người duyệt có. Nếu lập luận yếu, ai cũng có thể thấy là nó yếu.

Điều mà việc soạn nháp bằng AI không thể đem lại là sự tin cậy. Sự tin cậy ấy phải được gây dựng bởi những người đọc được ngôn ngữ gốc và đứng tên cho công việc của mình.

## Các bước duyệt

Một câu văn đi qua các trạng thái sau:

- **Bản nháp.** Được viết với AI, đã được phần mềm kiểm tra, nhưng chưa được người duyệt nào đọc.
- **Đã duyệt nghĩa.** Một học giả đọc được ngôn ngữ gốc, tiếng Hy Lạp cho Tân Ước và tiếng Hê-bơ-rơ cho Cựu Ước, đã kiểm tra các quyết định về nghĩa: bản văn nói gì.
- **Đã duyệt.** Một người duyệt ngôn ngữ, người đọc thông thạo ngôn ngữ mà câu văn được dịch sang, cũng đã kiểm tra lời văn.
- **Đã sửa sau khi duyệt.** Câu văn đã được thay đổi sau khi duyệt, với lý do được ghi lại.

Mỗi bước được ghi lại cùng tên người duyệt, ngày tháng và một ghi chú, để lịch sử của từng câu văn có thể được truy lại. Người duyệt cũng có thể báo một vấn đề hoặc để lại một nhận xét mà không chấp thuận gì cả. Việc nhập các bản nháp mới không bao giờ đặt lại trạng thái duyệt của một câu văn.

## Tình hình hiện nay

Các bản ghi về việc duyệt và vai trò của người duyệt đã có trong cơ sở dữ liệu của dự án, nhưng các công cụ mà người duyệt sẽ dùng vẫn đang được xây dựng. Cho đến khi chúng hoàn tất, các tệp trên GitHub là bản gốc của bản dịch, và mỗi câu văn giữ trạng thái của mình ở đó, trong dữ liệu mở.

Hiện nay chưa có câu văn nào trên trang này được duyệt. Mỗi câu, trong mọi ngôn ngữ, đều là một bản nháp được soạn với sự hỗ trợ của AI.

## Bạn có thể kiểm tra công việc như thế nào

Bạn không cần đợi người duyệt mới có thể thử thách điều mình đọc.

- **Mở bản ghi.** Chạm vào bất kỳ câu Kinh Thánh nào để xem bản dịch sát từng chữ, ba cấp độ và mọi quyết định của nó, cùng những phương án mà bản ghi đã cân nhắc.
- **Xem tiếng Hy Lạp hay tiếng Hê-bơ-rơ.** Chạm vào một chữ trong bảng để xem dạng từ điển, ngữ pháp và nghĩa của nó theo dữ liệu nguồn.
- **Tìm những lựa chọn sít sao.** Trang đọc có thể đánh dấu những chỗ ý nghĩa chưa chắc chắn, để bạn thấy ngay quyết định nào là những phán đoán cân nhắc.
- **So sánh các cấp độ.** Sát nghĩa cho thấy hình dáng của nguyên văn; Dễ đọc cho thấy chỗ nào bản dịch đã nói rõ ra một điều gì đó. Xin xem [Ba cấp độ, một ý nghĩa](/articles/three-levels-one-meaning/).
- **Đọc lịch sử.** Mọi bản ghi và mọi thay đổi trên đó đều có trên GitHub.

## Giúp duyệt

Nếu bạn đọc được tiếng Hy Lạp hay tiếng Hê-bơ-rơ, hoặc là người bản ngữ tiếng Tây Ban Nha, tiếng Pháp, tiếng Swahili, tiếng Việt hay tiếng Hàn có thể nhận ra một câu văn đọc có tự nhiên hay không, chúng tôi rất trân trọng sự giúp đỡ của bạn. Mọi thứ đều công khai trên [GitHub](https://github.com/jdegreef/open-word-bible), kể cả từng quyết định và lập luận của nó, và liên kết "Báo lỗi" ở cuối mỗi trang sẽ mở một vấn đề ở đó. Không đồng ý với một quyết định, và nói rõ vì sao, chính là kiểu giúp đỡ mà dự án cần.
