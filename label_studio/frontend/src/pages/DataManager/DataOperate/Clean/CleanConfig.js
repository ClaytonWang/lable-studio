import React, { forwardRef, useCallback, useContext, useEffect, useImperativeHandle, useRef, useState } from "react";
import { Modal } from "@/components/Modal/Modal";
import { Form, Select } from "antd";
import { Button } from "@/components";
// import { Select } from "@/components/Form/Elements";
import { find, get, isEmpty, orderBy } from "lodash";
import { ApiContext } from "@/providers/ApiProvider";
import { Space } from "@/components/Space/Space";
// import { PlusOutlined } from "@ant-design/icons";
// import { Icon } from "@/components/Icon/Icon";
// import { FaTrashAlt } from "react-icons/fa";

const formItemLayout = {
  labelCol: { span: 7 },
  wrapperCol: { span: 17 },
};

export const CleanConfig = forwardRef(({ cleanRefs }, ref) => {
  const api = useContext(ApiContext);
  const [cleanModels, setCleanModels] = useState([]);
  const [steps, setSteps] = useState([{ step: 1, value: null, status: null }]);
  const [value, setValue] = useState();

  const modalRef = useRef();

  useImperativeHandle(ref, () => ({
    show: () => {
      modalRef.current?.show();
    },
  }));

  const onHide = useCallback(async () => {
    modalRef?.current.hide(() => {
      setSteps([{ step: 1, value: null, status: null }]);
      localStorage.setItem('selectedCleanModel', '');
    });
  }, []);

  const handleChange = useCallback((v) => {
    setValue(v);
  }, []);

  useEffect(() => {
    const indexMap = {
      rule: 0,
      intelligent: 1,
      correction: 2,
    };
    
    const sortedValue = orderBy(value, item => {
      return get(indexMap, find(cleanModels, { id: item })?.type, 0);
    }, 'asc');

    window.__CLEAN_MODEL_VALUE = sortedValue;
  }, [cleanModels, value]);

  const addStep = useCallback((stp) => {
    setSteps(stp);
  }, []);

  const removeStep = useCallback((removedStp) => {
    let tmp = [...steps];

    tmp.splice(removedStp.step - 1, 1);

    tmp.forEach(v => {
      let sameIdx = tmp.findIndex(v => v.value === removedStp.value);

      if (sameIdx!==-1) {
        v.status=null;
      }
    });

    addStep(tmp);
  });

  const onChange = useCallback((index, value) => {
    let tmp = [...steps];

    tmp.forEach(v => {
      v.status=null;
    });

    let sameIdx = tmp.findIndex(v => v.value === value);

    if (sameIdx >= 0) {
      tmp.splice(index - 1, 1, { step: index, value, status: 'error' });
    } else {
      tmp.splice(index - 1, 1, { step: index, value, status: 'success' });
    }

    setSteps(tmp);
  }, [steps]);

  const getCleanModels = useCallback(async () => {
    return await api.callApi("modelManager", {
      params: { type: 'intelligent,rule,correction' },
    });
  }, []);

  // const onFinish = useCallback(() => {
  //   const modelIds = [];
  //   let errorCount = 0;
  //   let tmp = [...steps];

  //   tmp.forEach((v,i) => {
  //     tmp.forEach((t, n) => {
  //       if (!v.value || (v.value === t.value && i !== n)) {
  //         v.status = 'error';
  //         errorCount = errorCount+1;
  //       }
  //     });
  //   });

  //   if (errorCount > 0) {
  //     setSteps(tmp);
  //     return;
  //   } else {
  //     tmp.forEach(v => {
  //       modelIds.push(v.value);
  //     });
  //     localStorage.setItem('selectedCleanModel', modelIds.join(','));
  //     modalRef?.current.hide(() => {
  //       setSteps([{ step: 1, value: null, status: null }]);
  //     });
  //     cleanRefs?.current.show();
  //   }
  // },[steps]);

  const onFinish = useCallback(() => {
    if (isEmpty(window.__CLEAN_MODEL_VALUE)) {
      setSteps([{ step: 1, value: null, status: 'error' }]);
      return;
    }
    modalRef?.current.hide(() => {
      setSteps([{ step: 1, value: null, status: null }]);
    });
    cleanRefs?.current.show();
  }, []);

  useEffect(() => {
    getCleanModels().then(data => {
      // const rslt = ["", ...data?.results];
      const rslt = [...data?.results];

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
        清洗模型
      </Modal.Header>
      <Form
        {...formItemLayout}
        layout="horizontal"
        colon={false}
        style={{
          marginLeft: 24,
          marginTop: 24,
          marginBottom: 24,
        }}>
        {
          steps.map(stp => {
            return (
              <Form.Item key={stp.step}
                // label={`第${stp.step}步使用模型`}
                label="选择模型"
                validateStatus={stp.status}
                help={stp.status==='error' ? (!stp.value ? t("Please select Model type") : '不能选择相同的模型') : ''}
              >
                <Space>
                  <div style={{ width: 250 }}>
                    <Select
                      value={value}
                      size="large"
                      mode="multiple"
                      allowClear
                      placeholder={t("Please select Model type")}
                      options={cleanModels?.map(v => {
                        return { label: v.title_version, value: v.id };
                        // if (!v) {
                        //   return { label: t("Please select Model type"), value: '' };
                        // } else {
                        //   return { label: v.title_version, value: v.id };
                        // }
                      })}
                      onChange={handleChange} />
                  </div>
                  {/* {stp.step === 1 ? (
                    <Button
                      look="primary"
                      size="compact"
                      disabled={steps.length === 3 }
                      icon={<PlusOutlined />}
                      onClick={() => { addStep([...steps, { step: ++steps.length, value: '', status: null }]); }}
                      key="add_evaluate"
                    >
                      模型
                    </Button>
                  ) : null}
                  {stp.step === steps.length && stp.step !== 1 ? (
                    <a onClick={() => { removeStep(stp); }}>
                      <Icon icon={FaTrashAlt} />
                    </a>
                  ) : null} */}
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
