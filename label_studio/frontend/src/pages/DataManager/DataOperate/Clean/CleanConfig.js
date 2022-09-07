import React, { forwardRef, useCallback,useContext, useEffect,useImperativeHandle,useRef,useState } from "react";
import { Modal } from "@/components/Modal/Modal";
import { Form } from "antd";
import { Button } from "@/components";
import { Select } from "@/components/Form/Elements";
import { ApiContext } from "@/providers/ApiProvider";
import { Space } from "@/components/Space/Space";
import { PlusOutlined } from "@ant-design/icons";

const formItemLayout = {
  labelCol: { span: 7 },
  wrapperCol: { span: 17 },
};

export const CleanConfig = forwardRef((ref) => {
  const api = useContext(ApiContext);
  const [cleanModels, setCleanModels] = useState([]);
  const [steps, setSteps] = useState([1]);

  const modalRef = useRef();

  useImperativeHandle(ref, () => ({
    show: () => {
      modalRef.current?.show();
    },
  }));

  const onHide = useCallback(async () => {
    modalRef?.current.hide();
  }, []);

  const addStep = useCallback(async (stp) => {
    setSteps(stp);
  }, []);

  const getCleanModels = useCallback(async () => {
    return await api.callApi("modelManager", {
      params: { type:'clean' },
    });
  }, []);

  const onFinish = () => { };

  useEffect(() => {
    getCleanModels().then(data => {
      const rslt = ["",...data?.results];

      setCleanModels(rslt);
    });
  }, []);


  return (
    <Modal
      bare
      className="prediction-zone"
      ref={modalRef}
      style={{ width: 600 }}
      closeOnClickOutside={false}
    >
      <Modal.Header>
      清洗模型设置
      </Modal.Header>
      <Form
        {...formItemLayout}
        layout="horizontal"
        name="form_in_modal"
        className='modal_form'
        colon={false}
        style={{
          marginLeft: 24,
          marginTop: 24,
          marginBottom:24,
        }}>
        {
          steps.map(v => {
            return (
              <Form.Item key={v} label={ `第${v}步使用模型`}>
                <Space>
                  <div style={{ width: 250 }}>
                    <Select
                      options={cleanModels?.map(v => {
                        if (!v) {
                          return { label: t("Please select Model type"), value: '' };
                        } else {
                          return { label: v.title_version, value: v.id };
                        }
                      })}
                      onChange={(e) => {
                      }} />
                  </div>
                  { v===1 ? (
                    <Button
                      look="primary"
                      size="compact"
                      disabled={steps.length===3}
                      icon={<PlusOutlined />}
                      onClick={() => { addStep([...steps,++steps.length]);}}
                      key="add_evaluate"
                    >
                    模型
                    </Button>
                  ):null}
                </Space>
              </Form.Item>
            );
          })
        }

      </Form>
      <Modal.Footer>
        <Space align="end">
          <Button size="compact" onClick={onHide}>
            {t("Cancel")}
          </Button>
          <Button onClick={onFinish} size="compact" look="primary" >
            下一步
          </Button>
        </Space>
      </Modal.Footer>
    </Modal>
  );
});
