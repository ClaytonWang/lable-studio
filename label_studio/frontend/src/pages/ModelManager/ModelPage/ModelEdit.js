import React, { useCallback, useContext,useState } from 'react';
import { useHistory } from "react-router";
import { Modal } from '../../../components/Modal/Modal';
import { Form } from 'antd';
import { Button } from '../../../components';
import { Input } from '../../../components/Form';
import { ApiContext } from '../../../providers/ApiProvider';

export const ModelEdit = ({ data,onClose }) => {
  const api = useContext(ApiContext);
  const [form] = Form.useForm();
  const history = useHistory();
  const [waiting,setWaiting] = useState(false);

  const onHide = useCallback(async (force) => {
    history.replace("/model-manager");
    onClose?.(force);
  }, []);

  const layout = {
    labelCol: {
      span: 5,
    },
    wrapperCol: {
      span: 19,
    },
  };
  const tailLayout = {
    wrapperCol: {
      offset: 8,
      span: 16,
    },
  };

  const onFinish = async () => {
    setWaiting(true);
    try {
      const values = form.getFieldsValue(Object.keys(data));

      await api.callApi("editModel", {
        params: {
          pk: values.id,
        },
        body: values,
      });
      onHide(true);
    } catch (e) {
      console.error(e);
    } finally {
      setWaiting(false);
    }
  };

  return (
    <Modal style={{ width: 500 }}
      onHide={()=>onHide()}
      visible
      closeOnClickOutside={false}
      allowClose={true}
      title={t("Edit Model")}
    >
      <Form
        style={{ marginTop:20 }}
        initialValues={data}
        {...layout}
        form={form}
        layout="horizontal"
        name="form_in_modal"
        onFinish={ onFinish}
      >
        <Form.Item
          name="title"
          label="模型名称"
        >
          <Input disabled style={{ width:300 }} placeholder="模型名称"/>
        </Form.Item>

        <Form.Item
          name="model"
          label="模型集名称"
          rules={[
            {
              required: true,
              message: '请输入模型集名称。',
            },
          ]}
        >
          <Input style={{ width:300 }} placeholder="模型集名称"/>
        </Form.Item>
        <Form.Item {...tailLayout}>
          <Button
            size="compact"
            style={{
              margin: '0 8px',
            }}
            onClick={()=>onHide()}
            waiting={waiting}
          >
              取消
          </Button>
          <Button size="compact" look="primary" type="submit" waiting={waiting}>
              确定
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
};
