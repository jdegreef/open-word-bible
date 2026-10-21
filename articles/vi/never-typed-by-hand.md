---
title: Vì sao chúng tôi không bao giờ gõ tay tiếng Hy Lạp hay tiếng Hê-bơ-rơ
summary: Một quy tắc nghiêm ngặt bảo vệ sự chính xác của mọi thứ Open Word Bible trình bày từ các ngôn ngữ nguyên bản. Đây là quy tắc ấy, và cách phần mềm thực thi nó.
date: 2026-10-10
order: 9
section: method
source: f5bf26398aaa
---
Open Word Bible có một quy tắc khiến nhiều người ngạc nhiên: không ai, dù là con người hay AI, được gõ một chữ tiếng Hy Lạp hay tiếng Hê-bơ-rơ nào vào bản dịch hay vào các ghi chú của nó. Mọi chữ thuộc ngôn ngữ nguyên bản mà bạn thấy trên trang này, kể cả tiếng Hy Lạp và tiếng Hê-bơ-rơ trong các bài viết này, đều được phần mềm sao chép từ dữ liệu nguồn cố định.

## Vì sao

Tiếng Hy Lạp và tiếng Hê-bơ-rơ rất khó gõ cho đúng. Tiếng Hy Lạp có dấu nhấn và dấu hơi thở; tiếng Hê-bơ-rơ có dấu nguyên âm và dấu ngâm đọc. Nhiều dấu trông gần như y hệt nhau trên màn hình nhưng bên dưới lại là những ký tự khác nhau. Chữ omicron của tiếng Hy Lạp và chữ “o” của bảng chữ cái La-tinh trông giống hệt nhau trong phần lớn các phông chữ. Một số nguyên âm Hy Lạp có dấu nhấn có thể được lưu theo hai cách khác nhau nhưng hiển thị y như nhau. Một chữ được gõ theo trí nhớ có thể trông đúng mà vẫn sai: một dấu nhấn khác, một dấu hơi thở bị thiếu, một chữ cái hoàn toàn không có trong nguồn.

Trong giai đoạn thử nghiệm ban đầu, tiếng Hy Lạp được gõ theo trí nhớ đã chứa đúng những lỗi như thế. Một bản dịch tự nhận là trình bày cách mình làm việc thì không thể trình bày những chữ sai.

## Các nguồn

Bản văn đến từ những ấn bản cố định, có giấy phép mở, mỗi ấn bản được ghim vào một phiên bản chính xác để mọi kết quả đều có thể được tái lập:

- **Tân Ước:** bản Tân Ước Hy Lạp SBL (phiên bản 1.2), với dữ liệu từng chữ từ MACULA Greek.
- **Cựu Ước:** Codex Leningrad Westminster, với dữ liệu từ ngữ từ MACULA Hebrew và Open Scriptures Hebrew Bible.

“Được ghim” có nghĩa là hơn cả việc nêu tên một ấn bản. Dự án ghi lại chính xác bản sửa đổi của mỗi nguồn mà nó tải về, để bản văn không thể thay đổi bên dưới bản dịch mà không ai hay biết. Thông tin ghi công đầy đủ có ở trang [Giới thiệu](/about/).

## Quy tắc được thực thi thế nào

Quy tắc này không chỉ là một thói quen; phần mềm kiểm tra nó ở mỗi lần thay đổi.

- Bản văn nguyên ngữ của mỗi câu được dựng lại từ dữ liệu nguồn, và một câu có bản văn không khớp sẽ bị loại.
- Bất kỳ chữ tiếng Hy Lạp hay tiếng Hê-bơ-rơ nào ở bất kỳ chỗ nào khác, trong một bản dịch từng chữ, một bản dịch hay một ghi chú, đều phải khớp chính xác, từng ký tự một, với một dạng chữ hoặc một mục từ điển trong dữ liệu nguồn. Một chữ sai dấu nhấn sẽ không qua được bước kiểm tra.
- Các bài viết này trích tiếng Hy Lạp và tiếng Hê-bơ-rơ thông qua những chỗ giữ chỗ mà trang web điền vào từ dữ liệu khi được dựng. Khi bài này trình bày những chữ đầu tiên của sách Phúc Âm Giăng, {{GREEK:JHN.1.1:1-5}}, các chữ ấy đến từ dữ liệu của bản Tân Ước Hy Lạp SBL, chứ không phải từ một bàn phím.

Một chỗ giữ chỗ nêu tên một câu và một số thứ tự của chữ. Chữ đầu tiên của Sáng Thế Ký, {{HEBREW:GEN.1.1:1}}, được viết thành một chữ nhưng gồm hai phần: một tiền tố nghĩa là “trong” và danh từ “khởi đầu”. Một chỗ giữ chỗ có thể chỉ yêu cầu riêng phần thứ hai, ở dạng từ điển của nó, {{LEMMA:GEN.1.1:1.2}}. Hai dạng này trông không hoàn toàn giống nhau: dạng trong bản văn mang một dấu ngâm đọc dùng khi xướng tụng, còn dạng từ điển thì không. Nếu gõ tay, sự khác biệt ấy rất dễ làm sai. Nếu sao chép từ dữ liệu, nó không thể sai.

Những bước kiểm tra này chạy tự động trước khi bất cứ thứ gì được đăng. Một chỗ giữ chỗ trỏ đến một chữ tiếng Hy Lạp trong một câu Cựu Ước, hoặc đến một chữ không tồn tại, sẽ khiến trang web không dựng được.

## Những câu hỏi chính đáng

**Như vậy có phải bản văn nguồn không bao giờ được đặt câu hỏi?** Không. Bản văn nguồn không bao giờ bị sửa, nhưng bản dịch có thể không đồng ý với nó, một cách công khai. Ở Giăng 1:3, bản ghi đọc cách chấm câu khác với bản Tân Ước Hy Lạp SBL, và một quyết định giải thích lý do. Ở những chỗ các bản chép tay khác nhau, một quyết định mô tả cách đọc kia. Bản văn nền được giữ cố định để mọi chỗ đi khác với nó đều có thể thấy được.

**Một chữ đã được kiểm tra có bảo đảm một ghi chú đúng không?** Không. Bước kiểm tra chứng minh rằng một chữ thật sự có trong nguồn. Nó không thể chứng minh rằng một ghi chú nói đúng về chữ ấy. Đó là việc của những người duyệt là con người.
