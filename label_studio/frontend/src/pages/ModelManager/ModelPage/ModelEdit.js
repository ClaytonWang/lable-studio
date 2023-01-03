
import "codemirror/lib/codemirror.css";
import "codemirror/theme/material.css";
import "codemirror/mode/javascript/javascript.js";
import "codemirror/addon/display/placeholder.js";
import { UnControlled as CodeMirror } from 'react-codemirror2';
import React, { useCallback, useContext, useState } from "react";
import { useHistory } from "react-router";
import { Modal } from "../../../components/Modal/Modal";
import { Button ,Form } from "antd";
import { ApiContext } from "../../../providers/ApiProvider";
import "./ModelEdit.less";

export const ModelEdit = ({ data, onClose }) => {
  const api = useContext(ApiContext);
  const [form] = Form.useForm();
  const history = useHistory();
  const [waiting, setWaiting] = useState(false);

  const onHide = useCallback(async (force) => {
    history.replace("/model-manager");
    onClose?.(force, "edit");
  }, []);

  return (
    <Modal
      style={{ width: 800 }}
      onHide={() => onHide()}
      visible
      closeOnClickOutside={false}
      allowClose={true}
      title="编辑参数"
    >
      <div style={{ display: "json" }}>
        <CodeMirror
          name="code"
          id="model_edit_code"
          value=""
          options={{
            mode: {
              name: "javascript",
              json: true,
              statementIndent: 2,
            },
            theme: "material",
            lineNumbers: true,
            placeholder:"请输入正则表达式。。。",
          }}
          onChange={(editor, data, value) => {

          }}
        />
      </div>
      <div className="button-tail">
        <Button
          size="compact"
          style={{
            margin: "0 8px",
          }}
          onClick={() => onHide()}
          waiting={waiting}
        >
            取消
        </Button>
        <Button size="compact" type="primary" waiting={waiting}>
            确定
        </Button>
      </div>
    </Modal>
  );
};
