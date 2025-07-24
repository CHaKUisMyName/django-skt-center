/**
 * SweetAlert popup Message
 * @param {strign} mss - message detail
 * @param {strin} tag - tag success or error
 * @param {boolean} isRefresh - check location reload
 */
const PopMessage = (mss, tag, isRefresh = false, toURL = null) => {
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
  if (toURL) {
    popup.then(() => {
      window.location.href = toURL;
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
const initialDateTimePk = (element) => {
  const dp = new tempusDominus.TempusDominus(element, {
    useCurrent: false, // ไม่ให้มีค่าเริ่มต้นที่อาจผิดพลาด
    localization: {
      format: "dd/MM/yyyy HH:mm",
      hourCycle: "h24",
    },
    display: {
      // buttons: {
      //   today: true,
      //   clear: true,
      //   close: true,
      // },
      viewMode: "calendar",
      components: {
        decades: true,
        year: true,
        month: true,
        date: true,
        hours: true,
        minutes: true,
        seconds: false,
      },
    },
  });
  return dp;
};
const getAPIData = async (url) => {
  let returnData = null;
  const settings = {
    url: url,
    method: "GET",
  };
  await $.ajax(settings)
    .done((data) => {
      // console.log(data);
      if (data.success == true) {
        returnData = data.data;
      }
      Loading(false);
    })
    .fail((xhr, status, error) => {
      Loading(false);
      console.log(xhr.responseText);
    });
  return returnData;
};

/**
 * create dropdown jquery
 *
 * @param {List(obj)} data - list object
 * @param {string} name - name attr select
 * @returns
 */
const createDropdown = (data, name, selectedId = null) => {
  const select = $("<select>").addClass("form-select " + name);
  select.css({
    width: "100%",
  });
  select.prop("required", true);
  select.prop("name", name);
  $.each(data, (index, value) => {
    const option = $("<option>");
    option.val(value.id);
    option.text(
      "(" + value.code + ") " + value.nameEN + " (" + value.shortName + ")"
    );
    if (selectedId == value.id) {
      option.prop("selected", true);
    }
    select.append(option);
  });
  return select;
};

const createTableRole = (pos, orgs, seletedPos = null, seletedOrg = null) => {
  const posSelect = createDropdown(pos, "pos", seletedPos);
  const orgSelect = createDropdown(orgs, "org", seletedOrg);
  // -- div invalid feed back
  const invalidDiv = $("<div>").addClass("invalid-feedback");
  invalidDiv.text("Please select Data");
  const button = $("<button>", {
    type: "button",
    text: "Delete",
    class: "btn btn-danger delete",
  });
  // -- <td>
  const td = $("<td>");

  // -- td organization column
  const tdOrg = td.clone().append(orgSelect);
  tdOrg.append(invalidDiv.clone());
  // -- td position column
  const tdPos = td.clone().append(posSelect);
  tdPos.append(invalidDiv.clone());
  // -- td delete button column
  const tdDl = td.clone().append(button);
  // -- <tr>
  const tr = $("<tr>");
  tr.append(tdOrg);
  tr.append(tdPos);
  tr.append(tdDl);
  if (!$(".table > tbody")[0]) {
    const tbody = $("<tbody>");
    tbody.append(tr);
    const table = $(".table");
    table.append(tbody);
  } else {
    const table = $(".table > tbody");
    table.append(tr);
  }
};
