import React, { useCallback, useContext, useState } from 'react';
import { useHistory } from "react-router";
import { Modal } from '../../../components/Modal/Modal';
import { Form } from 'antd';
import { Button } from '../../../components';
import { Input } from '../../../components/Form';
import { ApiContext } from '../../../providers/ApiProvider';

export const AddEditOrganization = ({ onClose, data, type }) => {
  const api = useContext(ApiContext);
  const [form] = Form.useForm();
  const history = useHistory();
  const [waiting, setWaiting] = useState(false);

  const onHide = useCallback(async (force) => {
    history.replace("/organization/list");
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

      if (type === 'add') {
        await api.callApi("addOrg", {
          body: values,
        });
      } else {
        await api.callApi("updateOrg", {
          params: {
            pk: values.id,
          },
          body: values,
        });
      }

      onHide(true);
    } catch (e) {
      console.error(e);
    } finally {
      setWaiting(false);
    }
  };

  return (
    <Modal style={{ width: 500 }}
      onHide={() => onHide(false)}
      visible
      closeOnClickOutside={false}
      allowClose={true}
      title={type === 'type' ? t("add org") : t("edit org")}
    >
      <Form
        style={{ marginTop: 20 }}
        initialValues={data}
        {...layout}
        form={form}
        layout="horizontal"
        name="form_in_org"
        onFinish={onFinish}
        colon={false}
      >
        <Form.Item
          name="title"
          label="组织名称"
          rules={[
            {
              required: true,
              message: '请输入组织名称,且不能超过20个字符。',
            },
            { type: 'string', max: 20, min: 2 },
          ]}
        >
          <Input style={{ width: 300 }} placeholder="请输入组织名称" />
        </Form.Item>

        <Form.Item {...tailLayout}>
          <Button
            size="compact"
            style={{
              margin: '0 8px',
            }}
            onClick={() => onHide(false)}
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
