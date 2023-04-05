// <script>
//   $(document).ready(function() {
//     // 创建变量来跟踪折叠状态
//     var collapsed = {};
//     {% for record in records %}
//       collapsed[{{ record.id }}] = true;  // 初始值为 true，表示默认折叠
//     {% endfor %}
//
//     // 添加单击事件处理程序
//     $('.btn-primary').click(function() {
//       var record_id = $(this).next().attr('id').replace('items-', '');
//       collapsed[record_id] = !collapsed[record_id];  // 切换折叠状态
//       if (collapsed[record_id]) {
//         $(this).text('展开物品');
//         $('#items-' + record_id).collapse('hide');
//       } else {
//         $(this).text('折叠物品');
//         $('#items-' + record_id).collapse('show');
//       }
//     });
//
//     // 根据变量的值初始化记录的可见性
//     {% for record in records %}
//       if (collapsed[{{ record.id }}]) {
//         $('#items-{{ record.id }}').collapse('hide');
//       } else {
//         $('#items-{{ record.id }}').collapse('show');
//       }
//     {% endfor %}
//   });
