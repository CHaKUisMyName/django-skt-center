/**
 * SweetAlert popup Message
 * @param {strign} mss - message detail
 * @param {strin} tag - tag success or error
 * @param {boolean} isRefresh - check location reload
 */
const PopMessage = (mss, tag, isRefresh = false) => {
  const mssTag = tag;
  const mssMsg = mss;
  const mssHeader = mssTag == "error" ? "Error" : "Success";
  const mssIcon = mssTag == "error" ? "error" : "success";
  const popup = Swal.fire({
    icon: mssIcon,
    title: mssHeader,
    text: mssMsg,
    confirmButtonColor: "#f97316",
  });
  if (isRefresh == true) {
    popup.then(() => {
      location.reload();
    });
  }
};

// ฟังก์ชันเช็คว่า input มีค่าตรงกับ dd/mm/yyyy หรือไม่
function isValidDateFormat(dateString) {
  const regex = /^(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[0-2])\/\d{4}$/;
  return regex.test(dateString);
}

const initialDatePk = (element) => {
  const dp = new tempusDominus.TempusDominus(element, {
    useCurrent: false, // ไม่ให้มีค่าเริ่มต้นที่อาจผิดพลาด
    localization: {
      format: "dd/MM/yyyy",
      hourCycle: "h24",
    },
    display: {
      buttons: {
        today: true,
        clear: true,
        close: true,
      },
      //sideBySide: true,
      viewMode: "calendar",
      components: {
        decades: true,
        year: true,
        month: true,
        date: true,
        hours: false,
        minutes: false,
        seconds: false,
      },
    },
  });
  return dp;
};
